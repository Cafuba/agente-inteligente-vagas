# agente_visual.py
import os
import re
import threading
import time
from datetime import datetime
import urllib.parse
import webbrowser
import tkinter as tk
from tkinter import Tk, filedialog, messagebox, scrolledtext
from google import genai
from pypdf import PdfReader

# Configuração da Chave da API
os.environ["GEMINI_API_KEY"] = (
    "AQ.Ab8RN6KQeeJXNydu3Rwh4mO3IpS2WvkiqSCCGOb_tUf0xJq5EQ"
)

client = genai.Client()


def extrair_texto_pdf(caminho_do_pdf):
  try:
    leitor = PdfReader(caminho_do_pdf)
    texto_completo = ""
    for pagina in leitor.pages:
      texto_completo += pagina.extract_text() + "\n"
    return texto_completo
  except Exception as e:
    return None


def analisar_e_sugerir_vagas(texto_curriculo, max_tentativas=3):
  prompt = f"""
    Com base no currículo abaixo, atue como um recrutador especialista. Identifique o perfil do candidato e liste 5 excelentes opções de cargos/vagas alinhados com a experiência dele para o mercado do Rio de Janeiro.
    
    Para cada uma das 5 vagas, estime uma porcentagem realista de compatibilidade (de 0% a 100%) com base nas habilidades presentes no currículo.
    
    Retorne estritamente no seguinte formato, com um número por linha, sem textos adicionais desnecessários:
    1. Cargo: [Nome do Cargo] | Compatibilidade: [X]%
    2. Cargo: [Nome do Cargo] | Compatibilidade: [X]%
    3. Cargo: [Nome do Cargo] | Compatibilidade: [X]%
    4. Cargo: [Nome do Cargo] | Compatibilidade: [X]%
    5. Cargo: [Nome do Cargo] | Compatibilidade: [X]%
    
    CURRÍCULO:
    {texto_curriculo}
    """

  modelos = ["gemini-2.5-flash", "gemini-1.5-flash"]

  for modelo in modelos:
    for tentativa in range(1, max_tentativas + 1):
      try:
        response = client.models.generate_content(
            model=modelo, contents=prompt
        )
        return response.text
      except Exception as e:
        if "503" in str(e) and tentativa < max_tentativas:
          time.sleep(3)
          continue
        elif modelo != modelos[-1]:
          break

  return (
      "O servidor da IA está temporariamente sobrecarregado. Por favor, aguarde"
      " alguns segundos e tente novamente."
  )


class AppAgenteVagas:

  def __init__(self, root):
    self.root = root
    self.root.title("Agente Inteligente de Vagas 🚀")
    self.root.geometry("850x650")

    self.caminho_curriculo = ""
    self.texto_curriculo = ""

    titulo = tk.Label(
        root, text="Seu Assistente de Carreira IA", font=("Helvetica", 14, "bold")
    )
    titulo.pack(pady=10)

    
    frame_curriculo = tk.LabelFrame(
        root, text=" 1. Seu Currículo ", font=("Helvetica", 10, "bold")
    )
    frame_curriculo.pack(fill="x", padx=15, pady=5)

    self.btn_carregar = tk.Button(
        frame_curriculo,
        text="Selecionar Currículo (PDF)",
        command=self.carregar_curriculo,
        bg="#0066cc",
        fg="white",
        font=("Helvetica", 9, "bold"),
    )
    self.btn_carregar.pack(side="left", padx=10, pady=10)

    self.lbl_status = tk.Label(
        frame_curriculo,
        text="Nenhum currículo selecionado.",
        fg="red",
        font=("Helvetica", 9),
    )
    self.lbl_status.pack(side="left", padx=10, pady=10)

    self.frame_links = tk.LabelFrame(
        root,
        text=(
            " 2. Vagas Recomendadas e Compatibilidade Direta (Clique para"
            " buscar) "
        ),
        font=("Helvetica", 10, "bold"),
    )
    self.frame_links.pack(fill="both", expand=True, padx=15, pady=10)

    self.txt_links = scrolledtext.ScrolledText(
        self.frame_links, wrap=tk.WORD, height=18, font=("Helvetica", 10)
    )
    self.txt_links.pack(fill="both", expand=True, padx=10, pady=10)
    self.txt_links.insert(
        tk.END,
        "Selecione o seu currículo acima para analisar o perfil, calcular a"
        " compatibilidade automática e gerar os links de busca...",
    )
    self.txt_links.config(state=tk.DISABLED)

    
    self.txt_links.tag_config(
        "hyperlink", foreground="blue", underline=True
    )
    self.txt_links.tag_bind("hyperlink", "<Button-1>", self.clicar_link)
    self.txt_links.tag_bind(
        "hyperlink", "<Enter>", lambda e: self.txt_links.config(cursor="hand2")
    )
    self.txt_links.tag_bind(
        "hyperlink", "<Leave>", lambda e: self.txt_links.config(cursor="")
    )

  def carregar_curriculo(self):
    caminho = filedialog.askopenfilename(
        title="Selecione o seu Currículo (PDF)",
        filetypes=[("Arquivos PDF", "*.pdf")],
    )
    if caminho:
      self.caminho_curriculo = caminho
      nome_arquivo = os.path.basename(caminho)
      self.lbl_status.config(
          text=f"Carregado: {nome_arquivo}", fg="green"
      )

      self.texto_curriculo = extrair_texto_pdf(caminho)
      if self.texto_curriculo:
        self.txt_links.config(state=tk.NORMAL)
        self.txt_links.delete(1.0, tk.END)
        self.txt_links.insert(
            tk.END,
            "Analisando perfil e calculando compatibilidade com várias"
            " vagas...\nAguarde alguns segundos.",
        )
        self.txt_links.config(state=tk.DISABLED)
        self.btn_carregar.config(state=tk.DISABLED)

        threading.Thread(target=self.processar_ia_background, daemon=True).start()
      else:
        messagebox.showerror(
            "Erro", "Não foi possível extrair o texto do PDF."
        )

  def processar_ia_background(self):
    resposta_ia = analisar_e_sugerir_vagas(self.texto_curriculo)

    conteudo_final = (
        "=== VAGAS RECOMENDADAS E COMPATIBILIDADE ESTIMADA ===\n\n"
        + resposta_ia
        + "\n\n--- Links de Acesso Direto para Busca ---\n"
    )

    for linha in resposta_ia.split("\n"):
      if "Cargo:" in linha:
        try:
          cargo_nome = linha.split("Cargo:")[1].split("|")[0].strip()
          cargo_encoded = urllib.parse.quote(cargo_nome)
          link_linkedin = f"https://www.linkedin.com/jobs/search/?keywords={cargo_encoded}&location=Rio%20de%20Janeiro%2C%20Brazil"
          conteudo_final += (
              f"\n• {cargo_nome}\n  LinkedIn: {link_linkedin}\n"
          )
        except Exception:
          pass

    self.root.after(0, self.atualizar_interface, conteudo_final)

  def atualizar_interface(self, conteudo_final):
    self.txt_links.config(state=tk.NORMAL)
    self.txt_links.delete(1.0, tk.END)
    self.inserir_texto_com_links(conteudo_final)
    self.btn_carregar.config(state=tk.NORMAL)

  def inserir_texto_com_links(self, texto):
    padrao_url = r"(https?://[^\s\"'<>\)]+)"
    partes = re.split(padrao_url, texto)
    for pedaco in partes:
      if pedaco.startswith("http://") or pedaco.startswith("https://"):
        url_final = pedaco.rstrip(".,;:!?'\"")
        self.txt_links.insert(tk.END, url_final, "hyperlink")
      else:
        self.txt_links.insert(tk.END, pedaco)

  def clicar_link(self, event):
    try:
      index = self.txt_links.index(f"@{event.x},{event.y}")
      tag_ranges = self.txt_links.tag_ranges("hyperlink")
      for start, end in zip(tag_ranges[0::2], tag_ranges[1::2]):
        if (
            self.txt_links.compare(start, "<=", index)
            and self.txt_links.compare(index, "<=", end)
        ):
          url = self.txt_links.get(start, end)
          webbrowser.open(url)
          break
    except Exception as e:
      pass


if __name__ == "__main__":
  root = tk.Tk()
  app = AppAgenteVagas(root)
  root.mainloop()

  
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "SUA_CHAVE_AQUI")

