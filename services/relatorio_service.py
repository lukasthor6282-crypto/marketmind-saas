from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def gerar_relatorio_pdf(resultado, caminho="relatorio.pdf"):
    doc = SimpleDocTemplate(caminho)
    styles = getSampleStyleSheet()

    elementos = []

    elementos.append(Paragraph("Relatório de Análise de Mercado", styles["Title"]))
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph("Resumo Executivo:", styles["Heading2"]))
    elementos.append(Paragraph(resultado["resumo_executivo"], styles["Normal"]))
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph("Score:", styles["Heading2"]))
    elementos.append(Paragraph(str(resultado["score"]), styles["Normal"]))
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph("Palavras-chave:", styles["Heading2"]))
    elementos.append(Paragraph(str(resultado["palavras_chave"]), styles["Normal"]))
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph("Insights:", styles["Heading2"]))
    for insight in resultado["insights"]:
        elementos.append(Paragraph(f"- {insight}", styles["Normal"]))

    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph("Preço sugerido:", styles["Heading2"]))
    elementos.append(Paragraph(str(resultado["preco_sugerido"]), styles["Normal"]))

    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph("Faixa ideal:", styles["Heading2"]))
    elementos.append(Paragraph(str(resultado["faixa_ideal"]), styles["Normal"]))

    doc.build(elementos)

    return caminho