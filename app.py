from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from database import get_db_connection, init_db
from models import (
    Child, CreateChild, UpdateChild,
    AttendanceRow, UpsertAttendance,
    Route, Stats, HealthStatus
)

app = FastAPI(
    title="Sistema de Gestão de Transporte Escolar", 
    version="0.1.0", 
    description="API para controle de presença e otimização de rotas"
)

# Configuração de CORS - Permite que o Frontend se comunique com a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, substitua pelo domínio do seu app
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    """Inicializa o banco de dados ao subir a aplicação."""
    init_db()


# ── Health Check ─────────────────────────────────────────────────────────────

@app.get("/api/healthz", response_model=HealthStatus, tags=["Health"])
def health_check():
    return {"status": "ok"}


# ── Children (Alunos) ────────────────────────────────────────────────────────

@app.get("/api/children", response_model=list[Child], tags=["Children"])
def list_children():
    """Lista todos os alunos cadastrados em ordem alfabética."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, default_address, notes, shift, created_at 
                FROM children 
                ORDER BY name ASC
                """
            )
            rows = cur.fetchall()
    return [
        Child(
            id=r[0], name=r[1], defaultAddress=r[2],
            notes=r[3], shift=r[4], createdAt=r[5].isoformat()
        )
        for r in rows
    ]


@app.post("/api/children", response_model=Child, status_code=201, tags=["Children"])
def create_child(body: CreateChild):
    """Cadastra um novo aluno no sistema."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO children (name, default_address, notes, shift) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id, name, default_address, notes, shift, created_at
                """,
                (body.name.strip(), body.defaultAddress, body.notes, body.shift)
            )
            r = cur.fetchone()
        conn.commit()
    
    return Child(
        id=r[0], name=r[1], defaultAddress=r[2],
        notes=r[3], shift=r[4], createdAt=r[5].isoformat()
    )


@app.patch("/api/children/{child_id}", response_model=Child, tags=["Children"])
def update_child(child_id: int, body: UpdateChild):
    """Atualiza dados específicos de um aluno (Partial Update)."""
    fields = {}
    if body.name is not None:
        fields["name"] = body.name.strip()
    if body.defaultAddress is not None:
        fields["default_address"] = body.defaultAddress
    if body.notes is not None:
        fields["notes"] = body.notes
    if body.shift is not None:
        fields["shift"] = body.shift

    if not fields:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [child_id]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE children SET {set_clause} WHERE id = %s "
                f"RETURNING id, name, default_address, notes, shift, created_at",
                values
            )
            r = cur.fetchone()
        conn.commit()

    if not r:
        raise HTTPException(status_code=404, detail="Criança não encontrada")

    return Child(
        id=r[0], name=r[1], defaultAddress=r[2],
        notes=r[3], shift=r[4], createdAt=r[5].isoformat()
    )


@app.delete("/api/children/{child_id}", status_code=204, tags=["Children"])
def delete_child(child_id: int):
    """Remove um aluno do sistema."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM children WHERE id = %s", (child_id,))
        conn.commit()


# ── Attendance (Presença) ────────────────────────────────────────────────────

@app.get("/api/attendance", response_model=list[AttendanceRow], tags=["Attendance"])
def list_attendance(
    date: str = Query(..., description="Data no formato YYYY-MM-DD"),
    shift: Optional[str] = Query(None, description="Filtrar por turno (manhã/tarde)")
):
    """Lista a presença dos alunos em uma data específica."""
    params = [date]
    shift_filter = ""
    
    if shift:
        shift_filter = "AND c.shift = %s"
        params.append(shift)

    query = f"""
        SELECT c.id, c.name, c.default_address, c.shift,
               a.status, a.address
        FROM children c
        LEFT JOIN attendance a ON a.child_id = c.id AND a.date = %s
        WHERE 1=1 {shift_filter}
        ORDER BY c.name ASC
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

    return [
        AttendanceRow(
            childId=r[0],
            name=r[1],
            defaultAddress=r[2],
            shift=r[3],
            date=date,
            status=r[4] if r[4] else "unmarked",
            address=r[5]
        )
        for r in rows
    ]


@app.put("/api/attendance", response_model=AttendanceRow, tags=["Attendance"])
def upsert_attendance(body: UpsertAttendance):
    """Registra ou atualiza a presença de um aluno."""
    address_for_row = body.address if body.status == "present" else None

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Atualiza endereço padrão se marcado como presente com novo endereço
            if body.status == "present" and body.address and body.address.strip():
                cur.execute(
                    "UPDATE children SET default_address = %s WHERE id = %s",
                    (body.address.strip(), body.childId)
                )

            # Upsert na tabela de presença (Insere ou Atualiza se já existir)
            cur.execute(
                """
                INSERT INTO attendance (child_id, date, status, address)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (child_id, date)
                DO UPDATE SET status = EXCLUDED.status,
                              address = EXCLUDED.address,
                              updated_at = NOW()
                RETURNING child_id, date, status, address
                """,
                (body.childId, body.date, body.status, address_for_row)
            )
            att = cur.fetchone()

            # Busca dados atualizados da criança para o retorno
            cur.execute(
                "SELECT name, default_address, shift FROM children WHERE id = %s",
                (body.childId,)
            )
            child = cur.fetchone()
        conn.commit()

    return AttendanceRow(
        childId=att[0],
        name=child[0] if child else "",
        defaultAddress=child[1] if child else None,
        shift=child[2] if child else None,
        date=att[1],
        status=att[2],
        address=att[3]
    )


# ── Route (Otimização) ───────────────────────────────────────────────────────

@app.get("/api/route", response_model=Route, tags=["Route"])
def get_route(date: str = Query(...)):
    """Gera a lista de paradas para os alunos que estarão presentes no dia."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.id, c.name, 
                       COALESCE(a.address, c.default_address) AS address
                FROM attendance a
                INNER JOIN children c ON c.id = a.child_id
                WHERE a.date = %s AND a.status = 'present'
                ORDER BY c.name ASC
                """,
                (date,)
            )
            rows = cur.fetchall()

    stops = [
        {"childId": r[0], "name": r[1], "address": r[2]}
        for r in rows
        if r[2] and r[2].strip()
    ]

    return Route(date=date, stops=stops)


# ── Stats (Estatísticas) ─────────────────────────────────────────────────────

@app.get("/api/stats", response_model=Stats, tags=["Stats"])
def get_stats(date: str = Query(...)):
    """Retorna um resumo estatístico da presença no dia selecionado."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM children")
            total = cur.fetchone()[0]

            cur.execute(
                """
                SELECT COUNT(*) FROM children 
                WHERE default_address IS NOT NULL AND TRIM(default_address) != ''
                """
            )
            addresses_on_file = cur.fetchone()[0]

            cur.execute(
                """
                SELECT status, COUNT(*) FROM attendance 
                WHERE date = %s 
                GROUP BY status
                """,
                (date,)
            )
            status_rows = {r[0]: r[1] for r in cur.fetchall()}

    present = status_rows.get("present", 0)
    absent = status_rows.get("absent", 0)
    unmarked = max(0, total - present - absent)

    return Stats(
        date=date,
        totalChildren=total,
        presentCount=present,
        absentCount=absent,
        unmarkedCount=unmarked,
        addressesOnFile=addresses_on_file
    )
