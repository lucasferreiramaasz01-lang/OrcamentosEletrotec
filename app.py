import os
from flask import Flask, render_template, request, redirect, session, send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from PIL import Image as PILImage
import pillow_heif
from io import BytesIO

# Registrar suporte HEIC
pillow_heif.register_heif_opener()

app = Flask(__name__)
app.secret_key = "chave_super_secreta"

LOGIN_FIXO = "mauricio"
SENHA_FIXA = "12345"


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["login"] == LOGIN_FIXO and request.form["senha"] == SENHA_FIXA:
            session["logado"] = True
            return redirect("/form")
        else:
            return "Login incorreto!"
    return render_template("login.html")


# ================= FORMULÁRIO =================
@app.route("/form", methods=["GET", "POST"])
def form():
    if not session.get("logado"):
        return redirect("/")
    if request.method == "POST":
        return gerar_pdf()
    return render_template("form.html")


# ================= GERAR PDF =================
def gerar_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    # ===== LOGO NO TOPO =====
    logo_path = os.path.join("static", "logo.jpeg")

    if os.path.exists(logo_path):
        logo = PILImage.open(logo_path)

        largura_original, altura_original = logo.size
        largura_max = 200  # largura máxima da logo

        proporcao = largura_max / float(largura_original)
        nova_altura = float(altura_original) * proporcao

        logo_io = BytesIO()
        logo.save(logo_io, format="PNG")
        logo_io.seek(0)

        elements.append(Image(logo_io, width=largura_max, height=nova_altura))
        elements.append(Spacer(1, 20))

    # ===== DADOS DO FORMULÁRIO =====
    nome = request.form["nome"]
    endereco = request.form["endereco"]
    tipo = request.form["tipo"]
    tamanho = request.form["tamanho"]
    cor = request.form["cor"]
    descricao = request.form["descricao"]
    valor = request.form["valor"]
    pagamento = request.form["pagamento"]
    instalacao = request.form["instalacao"]

    elements.append(Paragraph("Proposta Comercial", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Cliente: {nome}", normal))
    elements.append(Paragraph(f"Endereço: {endereco}", normal))
    elements.append(Paragraph(f"Tipo de equipamento: {tipo}", normal))
    elements.append(Paragraph(f"Tamanho: {tamanho}", normal))
    elements.append(Paragraph(f"Cor: {cor}", normal))
    elements.append(Paragraph(f"Data de instalação: {instalacao}", normal))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Descrição do produto", styles["Heading3"]))
    elements.append(Paragraph(descricao, normal))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Condições de pagamento: {pagamento}", normal))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Valor: R$ {valor}", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    # ===== IMAGEM DO PRODUTO =====
    imagem = request.files["imagem"]

    if imagem:
        img = PILImage.open(imagem)

        largura_original, altura_original = img.size
        largura_max = 400  # largura máxima da imagem do produto

        proporcao = largura_max / float(largura_original)
        nova_altura = float(altura_original) * proporcao

        img_io = BytesIO()
        img.save(img_io, format="PNG")
        img_io.seek(0)

        elements.append(Image(img_io, width=largura_max, height=nova_altura))

    doc.build(elements)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="proposta.pdf",
        mimetype="application/pdf"
    )


# ================= EXECUÇÃO =================
if __name__ == "__main__":
    app.run()
