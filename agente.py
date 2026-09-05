# agente.py
import os
import time
from datetime import datetime
from tkinter import Tk, filedialog
from fpdf import FPDF
from google import genai
from pypdf import PdfReader

# Configuração da Chave da API
os.environ["GEMINI_API_KEY"] = (
    "AQ.Ab8RN6KQeeJXNydu3Rwh4mO3IpS2WvkiqSCCGOb_tUf0xJq5EQ"
)

client = genai.Client()


def selecionar_arquivo_pdf():
  print("\nPor favor, selecione o seu currículo na janela que apareceu...")
  root = Tk()
  root.withdraw()
  root.attributes("-topmost", True)
  caminho_arquivo = filedialog.askopenfilename(
      title="Selecione o seu Currículo (PDF)",
      filetypes=[("Arquivos PDF", "*.pdf")],
  )
  root.destroy()
  return caminho_arquivo


def extrair_texto_pdf(caminho_do_pdf):
  try:
    leitor = PdfReader(caminho_do_pdf)
    texto_completo = ""
    for pagina in leitor.pages:
      texto_completo += pagina.extract_text() + "\n"
    return texto_completo
  except Exception as e:
    print(f"Erro ao ler o arquivo PDF: {e}")
    return None


def gerar_links_de_vagas(texto_curriculo):
  prompt = f"""
    Com base no currículo abaixo, identifique o perfil profissional do candidato (áreas de atuação, cargos ideais e competências chaves).
    
    CURRÍCULO:
    {texto_curriculo}
    
    Gere uma resposta contendo:
    1. Um breve resumo de quais cargos combinam exatamente com esse perfil.
    2. Links diretos de busca no LinkedIn e Google Vagas para esses cargos.
    
    Formate os links de busca usando este padrão (substitua 'termo+da+busca' pelos cargos ideais):
    - LinkedIn: https://www.linkedin.com/jobs/search/?keywords=termo+da+busca
    - Google Vagas: https://www.google.com/search?q=vagas+de+termo+da+busca
    """
  try:
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    return response.text
  except Exception as e:
    print(f"Erro ao conectar com a IA: {e}")
    return None


def analisar_compatibilidade_com_retry(
    texto_curriculo, texto_vaga, max_tentativas=3
):
  prompt = f"""
    Você é um recrutador especialista em TI e Engenharia. 
    Analise o currículo abaixo e compare com a descrição da vaga fornecida.
    
    CURRÍCULO:
    {texto_curriculo}
    
    DESCRIÇÃO DA VAGA:
    {texto_vaga}
    
    Por favor, retorne uma resposta estruturada contendo exatamente:
    1. Nome do Cargo e Empresa (identificados na descrição da vaga).
    2. Link de busca direta: Crie um link de pesquisa no Google Vagas para o cargo exato e empresa informados, no formato: https://www.google.com/search?q=vagas+[cargo]+[empresa]
    3. Porcentagem de compatibilidade (0% a 100%).
    4. Pontos fortes (o que o candidato tem que a vaga pede).
    5. Gaps/O que falta (habilidades pedidas que não estão claras no currículo).
    6. Dica rápida para adaptar o currículo para essa vaga específica.
    """
  for tentativa in range(1, max_tentativas + 1):
    try:
      response = client.models.generate_content(
          model="gemini-2.5-flash", contents=prompt
      )
      return response.text
    except Exception as e:
      if tentativa == max_tentativas:
        raise e
      print(f"[AVISO] Servidor ocupado. Aguardando 15 segundos...")
      time.sleep(15)


def salvar_relatorio_pdf(resultado_analise):
  try:
    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"analise_compatibilidade_{data_hora}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(
        0,
        10,
        "RELATORIO DE COMPATIBILIDADE DA VAGA",
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
    )
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(
        0,
        10,
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
    )
    pdf.ln(10)

    pdf.set_font("Helvetica", size=11)
    texto_limpo = (
        resultado_analise.encode("latin-1", "replace").decode("latin-1")
    )
    pdf.multi_cell(0, 6, texto_limpo)

    pdf.output(nome_arquivo)
    print(
        f"\n[SUCESSO] Relatório de compatibilidade salvo em PDF: {nome_arquivo}"
    )
  except Exception as e:
    print(f"Erro ao gerar o arquivo PDF: {e}")


# --- EXECUÇÃO DO ECOSSISTEMA DO AGENTE ---

print("\n=== AGENTE INTELIGENTE: BUSCA + ANÁLISE DE VAGAS ===")
caminho_do_curriculo = selecionar_arquivo_pdf()

if caminho_do_curriculo:
  print("\n[PASSO 1] Lendo o seu currículo...")
  texto_do_currículo = extrair_texto_pdf(caminho_do_curriculo)

  if texto_do_currículo:
    print(
        "[PASSO 2] Mapeando perfil e gerando links personalizados de vagas..."
    )
    links_vagas = gerar_links_de_vagas(texto_do_currículo)

    print("\n==================================================")
    print("   LINKS GERADOS COM BASE NO SEU PERFIL   ")
    print("==================================================")
    print(links_vagas)
    print("==================================================\n")

    print(
        "Deseja fazer a análise de compatibilidade com alguma vaga encontrada"
        " agora?"
    )
    print("S - Sim, quero colar a descrição de uma vaga")
    print("N - Não, quero apenas os links por enquanto")
    opcao = input("> ").strip().upper()

    if opcao == "S":
      print(
          "\nExcelente! Cole aqui os requisitos/descrição da vaga (Pressione"
          " Enter duas vezes para finalizar):"
      )

      linhas_vaga = []
      while True:
        try:
          linha = input()
          if not linha and linhas_vaga and linhas_vaga[-1] == "":
            break
          linhas_vaga.append(linha)
        except EOFError:
          break
      vaga_colada = "\n".join(linhas_vaga)

      if vaga_colada.strip():
        print("\n[PASSO 3] Calculando compatibilidade com o Gemini...")
        resultado_analise = analisar_compatibilidade_com_retry(
            texto_do_currículo, vaga_colada
        )

        print("\n--- RELATÓRIO DE COMPATIBILIDADE ---")
        print(resultado_analise)

        print("\n[PASSO 4] Gerando PDF...")
        salvar_relatorio_pdf(resultado_analise)
      else:
        print("[AVISO] Nenhuma descrição foi informada.")
    else:
      print("\n[OK] Programa encerrado. Aproveite os links gerados acima!")

  else:
    print("[ERRO] Não foi possível ler o texto do currículo.")
else:
  print("[AVISO] Nenhum arquivo foi selecionado.")