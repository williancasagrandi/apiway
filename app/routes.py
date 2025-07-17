from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app import db
from app.models import Responsavel, Setor, Email, Obrigacao, StatusEmail
from app.email_sync import processar_emails
from app.sei_client import SEIClient
import requests

bp = Blueprint('routes', __name__)

# Armazena último status de sincronização
_last_sync = {"timestamp": None, "count": 0}

@bp.route("/responsaveis", methods=["POST"])
def criar_responsavel():
    data = request.get_json()
    novo = Responsavel(**data)
    try:
        db.session.add(novo)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(f"[DB] criar_responsavel: {e}")
        db.session.rollback()
        return jsonify(error="falha ao salvar responsável"), 500
    return jsonify(id=novo.id_responsavel), 201

@bp.route("/responsaveis", methods=["GET"])
def listar_responsaveis():
    q = Responsavel.query
    perfil = request.args.get("perfil")
    nome_like = request.args.get("nome_like")
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 20))

    if perfil:
        q = q.filter(Responsavel.tp_perfil == perfil)
    if nome_like:
        q = q.filter(Responsavel.nm_responsavel.ilike(f"%{nome_like}%"))

    pag = q.paginate(page=page, per_page=size, error_out=False)
    items = [
        {
            "id_responsavel": r.id_responsavel,
            "nm_responsavel": r.nm_responsavel,
            "email": r.email,
            "tp_perfil": r.tp_perfil.value
        }
        for r in pag.items
    ]
    return jsonify(page=pag.page, total=pag.total, items=items), 200

@bp.route("/responsaveis/<int:id>", methods=["GET"])
def obter_responsavel(id):
    r = Responsavel.query.get_or_404(id)
    return jsonify(
        id_responsavel=r.id_responsavel,
        nm_responsavel=r.nm_responsavel,
        email=r.email,
        tp_perfil=r.tp_perfil.value
    ), 200

@bp.route("/responsaveis/<int:id>", methods=["PUT"])
def atualizar_responsavel(id):
    data = request.get_json()
    r = Responsavel.query.get_or_404(id)
    for key in ("nm_responsavel", "email", "senha", "tp_perfil"):
        if key in data:
            setattr(r, key, data[key])
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(f"[DB] atualizar_responsavel: {e}")
        db.session.rollback()
        return jsonify(error="falha ao atualizar responsável"), 500
    return jsonify(message="responsável atualizado"), 200

@bp.route("/responsaveis/<int:id>", methods=["DELETE"])
def deletar_responsavel(id):
    r = Responsavel.query.get_or_404(id)
    try:
        db.session.delete(r)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(f"[DB] deletar_responsavel: {e}")
        db.session.rollback()
        return jsonify(error="falha ao deletar responsável"), 500
    return "", 204


@bp.route("/setores", methods=["POST"])
def criar_setor():
    data = request.get_json()
    novo = Setor(**data)
    try:
        db.session.add(novo)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(f"[DB] criar_setor: {e}")
        db.session.rollback()
        return jsonify(error="falha ao salvar setor"), 500
    return jsonify(id=novo.id_setor), 201

@bp.route("/setores", methods=["GET"])
def listar_setores():
    itens = [
        {"id_setor": s.id_setor, "nm_setor": s.nm_setor, "id_responsavel": s.id_responsavel}
        for s in Setor.query.all()
    ]
    return jsonify(items=itens), 200

@bp.route("/setores/<int:id>", methods=["GET"])
def obter_setor(id):
    s = Setor.query.get_or_404(id)
    return jsonify(id_setor=s.id_setor, nm_setor=s.nm_setor, id_responsavel=s.id_responsavel), 200

@bp.route("/setores/<int:id>", methods=["PUT"])
def atualizar_setor(id):
    data = request.get_json()
    s = Setor.query.get_or_404(id)
    if "nm_setor" in data:
        s.nm_setor = data["nm_setor"]
    if "id_responsavel" in data:
        s.id_responsavel = data["id_responsavel"]
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(f"[DB] atualizar_setor: {e}")
        db.session.rollback()
        return jsonify(error="falha ao atualizar setor"), 500
    return jsonify(message="setor atualizado"), 200

@bp.route("/setores/<int:id>", methods=["DELETE"])
def deletar_setor(id):
    s = Setor.query.get_or_404(id)
    try:
        db.session.delete(s)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(f"[DB] deletar_setor: {e}")
        db.session.rollback()
        return jsonify(error="falha ao deletar setor"), 500
    return "", 204

@bp.route("/emails", methods=["POST"])
def criar_email():
    data = request.get_json()
    novo = Email(**data)
    try:
        db.session.add(novo)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(f"[DB] criar_email: {e}")
        db.session.rollback()
        return jsonify(error="falha ao salvar email"), 500
    return jsonify(id=novo.id_email), 201

@bp.route("/emails", methods=["GET"])
def listar_emails():
    q = Email.query
    status = request.args.get("status")
    resp_id = request.args.get("responsavel")
    if status:
        q = q.filter(Email.tp_status == status)
    if resp_id:
        q = q.filter(Email.id_responsavel == int(resp_id))
    itens = [
        {
            "id_email": e.id_email,
            "assunto": e.assunto,
            "tp_status": e.tp_status.value,
            "id_responsavel": e.id_responsavel
        }
        for e in q.all()
    ]
    return jsonify(items=itens), 200

@bp.route("/emails/<int:id>", methods=["GET"])
def obter_email(id):
    e = Email.query.get_or_404(id)
    return jsonify(
        id_email=e.id_email,
        cd_sei=e.cd_sei,
        titulo=e.titulo,
        assunto=e.assunto,
        tp_status=e.tp_status.value,
        resposta=e.resposta,
        prazo_resposta=e.prazo_resposta.isoformat() if e.prazo_resposta else None,
        id_setor=e.id_setor,
        id_responsavel=e.id_responsavel,
        tp_email=e.tp_email
    ), 200

@bp.route("/emails/<int:id>", methods=["PUT"])
def atualizar_email(id):
    data = request.get_json()
    e = Email.query.get_or_404(id)
    for field in ("cd_sei","titulo","assunto","tp_status","resposta","prazo_resposta","id_setor","id_responsavel","tp_email"):
        if field in data:
            setattr(e, field, data[field])
    try:
        db.session.commit()
    except SQLAlchemyError as err:
        current_app.logger.error(f"[DB] atualizar_email: {err}")
        db.session.rollback()
        return jsonify(error="falha ao atualizar email"), 500
    return jsonify(message="email atualizado"), 200

@bp.route("/emails/<int:id>", methods=["DELETE"])
def deletar_email(id):
    e = Email.query.get_or_404(id)
    try:
        db.session.delete(e)
        db.session.commit()
    except SQLAlchemyError as err:
        current_app.logger.error(f"[DB] deletar_email: {err}")
        db.session.rollback()
        return jsonify(error="falha ao deletar email"), 500
    return "", 204

@bp.route("/emails/<int:id>/responder", methods=["POST"])
def responder_email(id):
    data = request.get_json()
    e = Email.query.get_or_404(id)
    e.resposta = data.get("resposta")
    e.tp_status = StatusEmail.RESPONDIDO
    try:
        db.session.commit()
    except SQLAlchemyError as err:
        current_app.logger.error(f"[DB] responder_email: {err}")
        db.session.rollback()
        return jsonify(error="falha ao responder email"), 500
    return jsonify(message="email respondido"), 200


@bp.route("/obrigacoes", methods=["POST"])
def criar_obrigacao():
    data = request.get_json()
    nova = Obrigacao(**data)
    try:
        db.session.add(nova)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(f"[DB] criar_obrigacao: {e}")
        db.session.rollback()
        return jsonify(error="falha ao salvar obrigação"), 500
    return jsonify(id=nova.id_obrigacao), 201

@bp.route("/obrigacoes", methods=["GET"])
def listar_obrigacoes():
    q = Obrigacao.query
    status = request.args.get("status")
    setor = request.args.get("setor")
    if status:
        q = q.filter(Obrigacao.tp_status == status)
    if setor:
        q = q.filter(Obrigacao.id_setor_atribuido == int(setor))
    itens = [
        {
            "id_obrigacao": o.id_obrigacao,
            "nm_tarefa": o.nm_tarefa,
            "tp_status": o.tp_status.value,
            "id_setor_atribuido": o.id_setor_atribuido
        }
        for o in q.all()
    ]
    return jsonify(items=itens), 200

@bp.route("/obrigacoes/<int:id>", methods=["GET"])
def obter_obrigacao(id):
    o = Obrigacao.query.get_or_404(id)
    return jsonify(
        id_obrigacao=o.id_obrigacao,
        nm_tarefa=o.nm_tarefa,
        tp_item=o.tp_item.value,
        tp_status=o.tp_status.value,
        id_setor_atribuido=o.id_setor_atribuido,
        id_area_condicionamento=o.id_area_condicionamento,
        periodicidade=o.periodicidade,
        dt_inicio=o.dt_inicio.isoformat() if o.dt_inicio else None,
        dt_termino=o.dt_termino.isoformat() if o.dt_termino else None,
        duracao=o.duracao,
        dt_limite=o.dt_limite.isoformat() if o.dt_limite else None,
        id_email=o.id_email
    ), 200

@bp.route("/obrigacoes/<int:id>", methods=["PUT"])
def atualizar_obrigacao(id):
    data = request.get_json()
    o = Obrigacao.query.get_or_404(id)
    for field in ("nm_tarefa","tp_item","tp_status","id_setor_atribuido","id_area_condicionamento","periodicidade","dt_inicio","dt_termino","duracao","dt_limite","id_email"):
        if field in data:
            setattr(o, field, data[field])
    try:
        db.session.commit()
    except SQLAlchemyError as err:
        current_app.logger.error(f"[DB] atualizar_obrigacao: {err}")
        db.session.rollback()
        return jsonify(error="falha ao atualizar obrigação"), 500
    return jsonify(message="obrigação atualizada"), 200

@bp.route("/obrigacoes/<int:id>", methods=["DELETE"])
def deletar_obrigacao(id):
    o = Obrigacao.query.get_or_404(id)
    try:
        db.session.delete(o)
        db.session.commit()
    except SQLAlchemyError as err:
        current_app.logger.error(f"[DB] deletar_obrigacao: {err}")
        db.session.rollback()
        return jsonify(error="falha ao deletar obrigação"), 500
    return "", 204


@bp.route("/obrigacoes/<int:id>/correspondencias", methods=["POST"])
def vincular_correspondencias(id):
    data = request.get_json()
    ids = data.get("emails", [])
    o = Obrigacao.query.get_or_404(id)
    for eid in ids:
        e = Email.query.get(eid)
        if e and e not in o.correspondencias:
            o.correspondencias.append(e)
    try:
        db.session.commit()
    except SQLAlchemyError as err:
        current_app.logger.error(f"[DB] vincular_correspondencias: {err}")
        db.session.rollback()
        return jsonify(error="falha ao vincular emails"), 500
    return jsonify(message="emails vinculados"), 200

@bp.route("/obrigacoes/<int:id>/correspondencias", methods=["GET"])
def listar_correspondencias(id):
    o = Obrigacao.query.get_or_404(id)
    items = [{"id_email": e.id_email, "assunto": e.assunto} for e in o.correspondencias]
    return jsonify(items=items), 200

@bp.route("/obrigacoes/<int:id>/correspondencias/<int:email_id>", methods=["DELETE"])
def desvincular_correspondencia(id, email_id):
    o = Obrigacao.query.get_or_404(id)
    e = Email.query.get_or_404(email_id)
    if e in o.correspondencias:
        o.correspondencias.remove(e)
        try:
            db.session.commit()
        except SQLAlchemyError as err:
            current_app.logger.error(f"[DB] desvincular_correspondencia: {err}")
            db.session.rollback()
            return jsonify(error="falha ao desvincular"), 500
    return "", 204



@bp.route("/sincronizar-emails", methods=["POST"])
def sincronizar_imap():
    try:
        count = processar_emails()
        _last_sync["timestamp"] = datetime.utcnow().isoformat()
        _last_sync["count"] = count
    except Exception as e:
        return jsonify(error=f"sincronização falhou: {e}"), 500
    return jsonify(processados=count), 200

@bp.route("/sincronizar-emails/status", methods=["GET"])
def status_sincronizacao():
    return jsonify(_last_sync), 200


sei = SEIClient()

@bp.route("/sei/interessado", methods=["GET"])
def rota_sei_interessado():
    nome = request.args.get("nome")
    orgao = int(request.args.get("orgao", 0))
    if not nome:
        return jsonify(error="parâmetro 'nome' obrigatório"), 400

    try:
        items = sei.pesquisar_por_interessado(nome, orgao)
    except requests.HTTPError as e:
        # registra status code e corpo para debugging
        status = e.response.status_code
        current_app.logger.error(f"[SEI] status {status}: {e.response.text[:200]}")
        return jsonify(error=f"SEI retornou {status}"), 502
    except Exception as e:
        current_app.logger.error(f"[SEI] exceção: {e}")
        return jsonify(error="falha na consulta SEI"), 502

    interessados = [row.get("Interessado") for row in items if "Interessado" in row]
    return jsonify(interessados=interessados), 200