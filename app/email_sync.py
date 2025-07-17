from imapclient import IMAPClient
import pyzmail
from flask import current_app
from app.models import db, Email, StatusEmail
import chardet

def processar_emails():
    cfg    = current_app.config
    host   = cfg["IMAP_HOST"]
    user   = cfg["EMAIL_USER"]
    pwd    = cfg["EMAIL_PASS"]
    folder = cfg.get("IMAP_FOLDER", "INBOX")

    processed = 0
    try:
        with IMAPClient(host) as server:
            server.login(user, pwd)
            server.select_folder(folder)
            uids = server.search(['UNSEEN'])

            for uid in uids:
                raw = server.fetch([uid], ['BODY[]'])[uid][b'BODY[]']
                msg = pyzmail.PyzMessage.factory(raw)
                assunto  = msg.get_subject()
                remetente = msg.get_addresses('from')[0][1]

                corpo = None
                if msg.text_part:
                    payload  = msg.text_part.get_payload()
                    encoding = msg.text_part.charset or chardet.detect(payload)['encoding']
                    corpo     = payload.decode(encoding, errors='replace')

                novo = Email(
                    titulo         = assunto,
                    assunto        = f"Email de {remetente}",
                    resposta       = corpo,
                    tp_status      = StatusEmail.RECEBIDO,
                    id_responsavel = 1
                )
                db.session.add(novo)
                processed += 1

            db.session.commit()
    except Exception as e:
        current_app.logger.error(f"[EMAIL] erro ao processar: {e}")
        db.session.rollback()
        raise

    return processed