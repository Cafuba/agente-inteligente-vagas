# 🚀 Agente Inteligente de Vagas IA

Assistente em Python com interface gráfica (Tkinter) que analisa currículos em PDF e recomenda automaticamente cargos compatíveis no mercado do Rio de Janeiro, com estimativa de compatibilidade e links de acesso direto para busca de vagas no LinkedIn.

## 🛠️ Tecnologias Utilizadas
- **Python 3.10+**
- **Tkinter** (Interface Gráfica Nativa)
- **Google Gemini API** (`google-genai`)
- **PyPDF** (Processamento e extração de texto de PDFs)
- **Threading** (Execução assíncrona para evitar travamentos da interface)

## 🎯 Funcionalidades
- Leitura automatizada de currículos em formato PDF.
- Análise preditiva de compatibilidade por cargo.
- Geração dinâmica de links formatados para busca no LinkedIn.
- Tratamento de exceções com tentativas de reconexão (503 retry) e fallback de modelos.
- Interface gráfica com suporte a links clicáveis e indicação visual de ponteiro.

## 📦 Como Executar o Projeto

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/Cafuba/agente-inteligente-vagas.git](https://github.com/Cafuba/agente-inteligente-vagas.git)
   cd agente-inteligente-vagas