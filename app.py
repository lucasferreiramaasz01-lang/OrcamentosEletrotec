import os
from flask import Flask, render_template, request, redirect, session, send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from PIL import Image as PILImage
import pillow_heif
from io import BytesIO

pillow_heif.register_heif_opener()

app = Flask(__name__)
app.secret_key = "chave_super_secreta"

LOGIN_FIXO = "mauricio"
SENHA_FIXA = "12345"


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["login"] == LOGIN_FIXO and request.form["senha"] == SENHA_FIXA:
            session["logado"] = True
            return redirect("/form")
        else:
            return "Login incorreto!"
    return render_template("login.html")


@app.route("/form", methods=["GET", "POST"])
def form():
    if not session.get("logado"):
        return redirect("/")
    if request.method == "POST":
        return gerar_pdf()
    return render_template("form.html")


def gerar_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    bold = styles["Heading2"]

    # ===== LOGO =====
    logo_path = os.path.join("static", "logo.jpeg")
    if os.path.exists(logo_path):
        logo = PILImage.open(logo_path)
        largura, altura = logo.size
        largura_max = 250
        proporcao = largura_max / float(largura)
        nova_altura = float(altura) * proporcao

        logo_io = BytesIO()
        logo.save(logo_io, format="PNG")
        logo_io.seek(0)

        elements.append(Image(logo_io, width=largura_max, height=nova_altura))
        elements.append(Spacer(1, 20))

    elements.append(Paragraph("Proposta Comercial", styles["Title"]))
    elements.append(Spacer(1, 20))

    # ===== DADOS =====
    nome = request.form["nome"]
    endereco = request.form["endereco"]
    tipo = request.form["tipo"]
    tamanho = request.form["tamanho"]
    cor = request.form["cor"]
    descricao = request.form["descricao"]
    valor = request.form["valor"]
    pagamento = request.form["pagamento"]
    instalacao = request.form["instalacao"]

    dados = [
        ["Cliente:", nome],
        ["Endereço:", endereco],
        ["Tipo de equipamento:", tipo],
        ["Tamanho:", tamanho],
        ["Data de instalação:", instalacao],
    ]

    tabela_dados = Table(dados, colWidths=[170, 300])
    tabela_dados.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke)
    ]))

    elements.append(tabela_dados)
    elements.append(Spacer(1, 20))

    # ===== DESCRIÇÃO =====
    elements.append(Paragraph("Descrição do produto", bold))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(descricao, normal))
    elements.append(Spacer(1, 20))

    # ===== PAGAMENTO =====
    elements.append(Paragraph(f"Condições de pagamento: {pagamento}", normal))
    elements.append(Spacer(1, 20))

    # ===== VALOR (2 VEZES COMO NO MODELO) =====
    elements.append(Paragraph(f"Valor: R$ {valor}", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Valor: R$ {valor}", styles["Heading2"]))
    elements.append(Spacer(1, 30))

    # ===== IMAGEM DO PRODUTO =====
    imagem = request.files["imagem"]
    if imagem:
        img = PILImage.open(imagem)
        largura, altura = img.size
        largura_max = 400
        proporcao = largura_max / float(largura)
        nova_altura = float(altura) * proporcao

        img_io = BytesIO()
        img.save(img_io, format="PNG")
        img_io.seek(0)

        elements.append(Paragraph("Imagem do produto", bold))
        elements.append(Spacer(1, 10))
        elements.append(Image(img_io, width=largura_max, height=nova_altura))
        elements.append(Spacer(1, 40))

    # ===== ASSINATURA =====
    elements.append(Paragraph("Assinatura do responsável", normal))

    doc.build(elements)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="proposta.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run()
