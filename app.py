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

        if logo.mode != "RGB":
            logo = logo.convert("RGB")

        logo.thumbnail((800, 800))

        largura, altura = logo.size
        largura_max = 200
        proporcao = largura_max / float(largura)
        nova_altura = float(altura) * proporcao

        logo_io = BytesIO()
        logo.save(logo_io, format="JPEG", quality=85, optimize=True)
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
    elements.append(Spacer(1, 15))

    # ===== VALOR (AGORA APENAS 1 VEZ) =====
    elements.append(Paragraph(f"<b>Valor: R$ {valor}</b>", normal))
    elements.append(Spacer(1, 25))

    # ===== IMAGEM DO PRODUTO (MENOR E À DIREITA) =====
    imagem = request.files["imagem"]

    if imagem:
        img = PILImage.open(imagem)

        if img.mode != "RGB":
            img = img.convert("RGB")

        img.thumbnail((1000, 1000))

        largura, altura = img.size

        # 🔥 reduzir 25% mantendo proporção
        largura_pdf = 300
        proporcao = largura_pdf / float(largura)
        nova_altura = float(altura) * proporcao

        img_io = BytesIO()
        img.save(img_io, format="JPEG", quality=85, optimize=True)
        img_io.seek(0)

        img_prod = Image(img_io, width=larga_pdf if False else largura_pdf, height=nova_altura)
        img_prod.hAlign = "RIGHT"

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
