import os
from flask import Flask, render_template, request, redirect, session, send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
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
    doc = SimpleDocTemplate(
        buffer,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    elements = []

    normal = ParagraphStyle(
        name="NormalStyle",
        fontName="Helvetica",
        fontSize=12,
        spaceAfter=6
    )

    titulo = ParagraphStyle(
        name="TituloStyle",
        fontName="Helvetica-Bold",
        fontSize=16,
        spaceAfter=15
    )

    # ===== LOGO =====
    logo_path = os.path.join("static", "logo.jpeg")
    if os.path.exists(logo_path):
        logo = PILImage.open(logo_path)
        largura, altura = logo.size
        largura_max = 220
        proporcao = largura_max / float(largura)
        nova_altura = float(altura) * proporcao

        logo_io = BytesIO()
        logo.save(logo_io, format="PNG")
        logo_io.seek(0)

        img_logo = Image(logo_io, width=largura_max, height=nova_altura)
        img_logo.hAlign = "CENTER"
        elements.append(img_logo)
        elements.append(Spacer(1, 20))

    # ===== TÍTULO =====
    elements.append(Paragraph("Proposta Comercial", titulo))
    elements.append(Spacer(1, 10))

    # ===== DADOS =====
    nome = request.form["nome"]
    endereco = request.form["endereco"]
    tipo = request.form["tipo"]
    tamanho = request.form["tamanho"]
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

    tabela = Table(dados, colWidths=[180, 330])
    tabela.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))

    elements.append(tabela)
    elements.append(Spacer(1, 20))

    # ===== DESCRIÇÃO =====
    elements.append(Paragraph("Descrição do produto", normal))
    elements.append(Paragraph(descricao, normal))
    elements.append(Spacer(1, 20))

    # ===== PRODUTO =====
    elements.append(Paragraph("Produto", normal))
    elements.append(Spacer(1, 5))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 20))

    # ===== PAGAMENTO =====
    elements.append(Paragraph(f"Condições de pagamento: {pagamento}", normal))
    elements.append(Spacer(1, 20))

    # ===== VALOR DUPLICADO =====
    elements.append(Paragraph(f"Valor: R$ {valor}", normal))
    elements.append(Paragraph(f"Valor: R$ {valor}", normal))
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

        elements.append(Paragraph("Imagem do produto", normal))
        elements.append(Spacer(1, 10))

        img_prod = Image(img_io, width=largura_max, height=nova_altura)
        img_prod.hAlign = "LEFT"
        elements.append(img_prod)
        elements.append(Spacer(1, 40))

    # ===== ASSINATURA =====
    elements.append(HRFlowable(width="50%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 5))
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
