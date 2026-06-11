from flask import current_app
from flask_mail import Message
from app import mail


def stuur_bevestigingsmail(order):
    if not current_app.config.get('MAIL_USERNAME'):
        current_app.logger.info('MAIL_USERNAME niet ingesteld – bevestigingsmail overgeslagen.')
        return

    verzend_kosten = 4.99 if order.verzendmethode == 'express' else 0.0
    totaal_incl    = order.totaal() + verzend_kosten
    verzend_str    = '€4,99' if order.verzendmethode == 'express' else 'Gratis'

    regels_html = ''.join(
        f'<tr>'
        f'<td style="padding:6px 12px">{r.product.naam if r.product else "(verwijderd)"}</td>'
        f'<td style="text-align:center;padding:6px 12px">{r.aantal}×</td>'
        f'<td style="text-align:right;padding:6px 12px">€{"%.2f" % (r.prijs_per_stuk * r.aantal)}</td>'
        f'</tr>'
        for r in order.regels
    )

    html = f"""
    <div style="font-family:Nunito,sans-serif;max-width:600px;margin:auto;color:#1e1b4b">
      <div style="background:#7c3aed;padding:28px 32px;border-radius:12px 12px 0 0;text-align:center">
        <h1 style="color:#fff;margin:0;font-size:1.6rem">&#128156; Little Wings</h1>
        <p style="color:#e9d5ff;margin:6px 0 0">Play &middot; Heal &middot; Fly</p>
      </div>

      <div style="background:#fff;padding:32px;border:1px solid #e8e0f5;border-top:none;border-radius:0 0 12px 12px">
        <h2 style="color:#7c3aed;margin-top:0">Bedankt voor je bestelling, {order.klant_naam}!</h2>
        <p>We hebben je bestelling ontvangen en gaan er meteen mee aan de slag.</p>

        <h3 style="color:#4c1d95;border-bottom:2px solid #e8e0f5;padding-bottom:8px">
          Jouw bestelling #{order.id}
        </h3>
        <table style="width:100%;border-collapse:collapse;font-size:.95rem">
          <thead>
            <tr style="background:#f5f3ff">
              <th style="text-align:left;padding:8px 12px;color:#6b21a8">Product</th>
              <th style="text-align:center;padding:8px 12px;color:#6b21a8">Aantal</th>
              <th style="text-align:right;padding:8px 12px;color:#6b21a8">Subtotaal</th>
            </tr>
          </thead>
          <tbody style="border-top:1px solid #e8e0f5">
            {regels_html}
            <tr style="border-top:1px solid #e8e0f5">
              <td colspan="2" style="padding:6px 12px;color:#888">
                Verzendkosten ({order.verzendmethode})
              </td>
              <td style="text-align:right;padding:6px 12px;color:#888">{verzend_str}</td>
            </tr>
            <tr style="border-top:2px solid #e8e0f5;font-weight:700">
              <td colspan="2" style="padding:10px 12px;font-size:1.05rem">Totaal</td>
              <td style="text-align:right;padding:10px 12px;color:#7c3aed;font-size:1.1rem">
                &euro;{"%.2f" % totaal_incl}
              </td>
            </tr>
          </tbody>
        </table>

        <h3 style="color:#4c1d95;border-bottom:2px solid #e8e0f5;padding-bottom:8px;margin-top:28px">
          Bezorgadres
        </h3>
        <p style="line-height:1.8;margin:0">
          {order.klant_naam}<br>
          {order.straat or ''}<br>
          {order.postcode or ''} {order.stad or ''}<br>
          {order.land or ''}
        </p>
        <p style="margin-top:8px;color:#888;font-size:.9rem">
          Betaalmethode: {order.betaalmethode or '&ndash;'}
        </p>

        <div style="background:#f5f3ff;border-radius:8px;padding:16px;margin-top:28px;text-align:center">
          <p style="margin:0;color:#6b21a8;font-size:.9rem">
            Met elke aankoop steun je <strong>kinderen getroffen door oorlog</strong>.<br>
            Bedankt voor je bijdrage! &#128570;
          </p>
        </div>
      </div>
    </div>
    """

    msg = Message(
        subject=f'Bevestiging bestelling #{order.id} – Little Wings',
        recipients=[order.klant_email],
        html=html,
    )
    try:
        mail.send(msg)
        current_app.logger.info(f'Bevestigingsmail verstuurd naar {order.klant_email}')
    except Exception as exc:
        current_app.logger.error(f'Bevestigingsmail mislukt voor order #{order.id}: {exc}')
