from imapclient import IMAPClient
import pyzmail
from flask import current_app
from app.models import db, Email, StatusEmail
import chardet
import ssl

def processar_emails():
    cfg    = current_app.config
    logger = current_app.logger
    host   = cfg["IMAP_HOST"]
    port   = cfg.get("IMAP_PORT", 993)
    user   = cfg["EMAIL_USER"]
    pwd    = cfg["EMAIL_PASS"]
    folder = cfg.get("IMAP_FOLDER", "INBOX")

    ssl_ctx = ssl._create_unverified_context()

    processed = 0
    logger.info(f"[EMAIL] Iniciando processamento de emails em {host}:{port}, pasta '{folder}'")
    try:
        with IMAPClient(host, port=port, ssl=True, ssl_context=ssl_ctx) as server:
            logger.debug("[EMAIL] Conectado ao servidor IMAP, realizando login")
            server.login(user, pwd)
            logger.debug(f"[EMAIL] Logado como '{user}', selecionando pasta '{folder}'")
            server.select_folder(folder)

            uids = server.search(['UNSEEN'])
            logger.info(f"[EMAIL] Encontrados {len(uids)} emails não lidos")

            for uid in uids:
                logger.debug(f"[EMAIL] Processando email UID {uid}")
                raw = server.fetch([uid], ['BODY[]'])[uid][b'BODY[]']
                msg = pyzmail.PyzMessage.factory(raw)

                assunto   = msg.get_subject()
                remetente = msg.get_addresses('from')[0][1]
                logger.debug(f"[EMAIL] Assunto: '{assunto}', Remetente: '{remetente}'")

                corpo = None
                if msg.text_part:
                    payload  = msg.text_part.get_payload()
                    encoding = msg.text_part.charset or chardet.detect(payload)['encoding']
                    corpo     = payload.decode(encoding, errors='replace')
                    logger.debug(f"[EMAIL] Corpo decodificado (100 primeiros chars): {corpo[:100]!r}")
                    print(f"[EMAIL] Corpo completo do email UID {uid}:\n{corpo}")

                novo = Email(
                    cd_sei        = None,
                    remetente     = remetente,
                    assunto       = assunto,
                    conteudo      = corpo,
                    resposta      = None,
                    tp_status     = StatusEmail.RECEBIDO,
                    id_setor      = None,
                    id_responsavel= 1,
                    tp_email      = None
                )
                db.session.add(novo)
                processed += 1

            db.session.commit()
            logger.info(f"[EMAIL] Processamento concluído. Total processados: {processed}")

    except Exception as e:
        logger.error(f"[EMAIL] Erro ao processar emails: {e}", exc_info=True)
        db.session.rollback()
        raise

    return processed
