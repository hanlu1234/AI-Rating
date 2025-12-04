"""
AI Product Content Evaluator
评估优化后的商品title和description是否符合标准
"""

import csv
import json
import os
import re
from typing import Dict, List, Tuple, Optional
import dashscope
from dashscope import Generation
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ProductContentEvaluator:
    """商品内容评估器"""
    
    def __init__(self, api_key: str = None, model: str = "qwen-plus"):
        """初始化评估器
        
        Args:
            api_key: DashScope API Key
            model: 使用的模型名称，默认为 qwen-plus，可选 qwen-turbo, qwen-max 等
        """
        self.api_key = api_key or os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("API Key未设置，请通过参数传入或设置环境变量QWEN_API_KEY或DASHSCOPE_API_KEY")
        dashscope.api_key = self.api_key
        self.model = model
        
        # Title评估标准
        self.title_requirements = {
            "must_have": [
                "Clear Product Type: The Title must name the product type (e.g., 'Laptop Lenovo', 'Water Bottle') as stated in the original Title&Description.",
                "Key Details (if Available in Title&Description): Include additional specifications (e.g., size, material, brand, certificate, application) from the original Title or Description."
            ],
            "must_avoid": [
                "No Extra Details: Don't add information not in the original.",
                "No Repetition or Stuffing: Avoid repeating words or synonym keywords (e.g., 'Steel Metal Bottle Steel').",
                "Short and Clear: Keep Title between 3-128 characters (ideal 50-80). Start with product type, then specs.",
                "No Forbidden Content: Don't include prices, VAT, shipping, company names, or incomplete phrases (e.g., ending in 'for', 'and').",
                "No Brand/Model Only: Title can't be just a brand or model number—include product type."
            ]
        }
        
        # Description评估标准
        self.description_requirements = {
            "must_have": [
                "Match Title and Original: The Description must use the same details as the Title and original text, with no contradictions.",
                "Key Details Upfront: Include product type and key specs (if available) in the first sentence.",
                "Clear Structure (if Enough Info): Intro sentence (type + specs). Bullet points (list features, materials, etc.). Conclusion (value/use, if in original).",
                "Proper Length: 1 = Input too little text/terms → Output description may be <601 chars; focus on clarity & accuracy. 2 = Input sufficient text/terms → Output description must be >610 chars (aim 610–700). 3 = Input too much text/terms → Output description must be 600–700 chars; condense & remove redundancy."
            ],
            "must_avoid": [
                "No Extra Details: Don't add benefits, use cases, marketing info or specs not in the original.",
                "No Repetition or Stuffing: Avoid repeating words or overloading keywords.",
                "No Forbidden Content: Don't include prices, VAT, shipping, company/project info, or incomplete phrases.",
                "No Care Tips or Extras: Don't add recipes, maintenance advice, or unsupported claims."
            ]
        }
    
    def detect_language(self, text: str) -> str:
        """检测文本语言"""
        if not text or not text.strip():
            return "en"
        
        # 检测中文字符
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        if chinese_pattern.search(text):
            return "zh"
        
        # 检测德文特征字符（德文特有字符：ä, ö, ü, ß）
        german_chars = re.compile(r'[äöüÄÖÜß]')
        if german_chars.search(text):
            return "de"
        
        # 检测常见德文词汇（商品描述中常见的德文词）
        common_german_words = [
            'der', 'die', 'das', 'und', 'ist', 'sind', 'für', 'mit', 'auf', 'in', 'zu', 'von',
            'über', 'unter', 'nach', 'vor', 'bei', 'durch', 'gegen', 'ohne', 'um', 'an', 'als',
            'wie', 'wenn', 'dass', 'wird', 'werden', 'kann', 'können', 'muss', 'müssen',
            'hat', 'haben', 'wurde', 'wurden', 'sein', 'seine', 'ihr', 'ihre',
            'produkt', 'artikel', 'ware', 'marke', 'hersteller', 'modell', 'typ', 'version',
            'qualität', 'material', 'größe', 'farbe', 'preis', 'kosten', 'versand', 'lieferung',
            'bestellung', 'kauf', 'verkauf', 'verfügbar', 'erhältlich', 'lager', 'vorrätig',
            'empfehlung', 'bewertung', 'kunde', 'service', 'garantie', 'rückgabe', 'umtausch',
            'versandkosten', 'zahlung', 'rechnung', 'lieferzeit', 'verfügbarkeit', 'rabatt',
            'angebot', 'sonderangebot', 'neuheit', 'bestseller', 'beliebt', 'trend',
            'technologie', 'technisch', 'elektronik', 'elektrisch', 'digital', 'automatisch',
            'kompatibel', 'zubehör', 'optional', 'standard', 'premium', 'professionell',
            'haushalt', 'büro', 'geschäft', 'industrie', 'sport', 'fitness', 'gesundheit',
            'design', 'funktion', 'funktional', 'eigenschaft', 'merkmal', 'vorteil'
        ]
        
        text_lower = text.lower()
        german_word_count = sum(1 for word in common_german_words if word in text_lower)
        
        # 如果包含多个德文常见词，判定为德文
        if german_word_count >= 3:
            return "de"
        
        # 默认返回英文
        return "en"
    
    def evaluate_title(self, original_title: str, original_description: str, 
                      optimized_title: str, source_lang: str = "en") -> Dict:
        """评估Title"""
        
        # 根据源语言选择prompt语言
        if source_lang == "de":
            prompt = f"""Sie sind ein Experte für die Bewertung von Produkttiteln. Bitte bewerten Sie den optimierten Titel nach folgenden Kriterien.

Originaltitel: {original_title}
Originalbeschreibung: {original_description}
Optimierter Titel: {optimized_title}

Bewertungskriterien:

Erforderliche Anforderungen (Must Have):
1. Klarer Produkttyp: Der Titel muss den Produkttyp enthalten (z.B. "Laptop Lenovo", "Wasserflasche") und muss mit dem im Originaltitel und in der Beschreibung genannten Produkttyp übereinstimmen.
2. Wichtige Details: Wenn es zusätzliche Spezifikationen im Originaltitel oder in der Beschreibung gibt (wie Größe, Material, Marke, Zertifikat, Anwendung), sollten diese im optimierten Titel enthalten sein.

Zu vermeidende Probleme (Must Avoid):
1. Keine zusätzlichen Details: Fügen Sie keine Informationen hinzu, die nicht im Originalinhalt vorhanden sind.
2. Keine Wiederholung oder Überladung: Vermeiden Sie wiederholte Wörter oder Synonym-Keyword-Stuffing (z.B. "Stahl Metall Flasche Stahl").
3. Kurz und klar: Die Titelänge sollte zwischen 3-128 Zeichen liegen (ideal 50-80 Zeichen). Sollte mit dem Produkttyp beginnen, gefolgt von Spezifikationen.
4. Keine verbotenen Inhalte: Enthalten Sie keine Preise, Mehrwertsteuer, Versand, Firmennamen oder unvollständige Phrasen (z.B. endend mit "für", "und").
5. Nicht nur Marke/Modell: Der Titel darf nicht nur eine Marke oder Modellnummer sein—muss den Produkttyp enthalten.

Bewertungssystem:
- Für "Must Have" Kriterien: 0=erfüllt nicht, 1=teilweise erfüllt, 2=vollständig erfüllt
- Für "Must Avoid" Kriterien: 0=Problem vorhanden (Kriterium verletzt), 1=teilweise Problem, 2=kein Problem (Kriterium vollständig eingehalten)

Bitte bewerten Sie jedes Kriterium entsprechend und geben Sie detaillierte Bewertungsergebnisse.

WICHTIG: Alle "reason" und "overall_reason" Felder müssen auf Englisch geschrieben werden.

Ausgabeformat als JSON:
{{
    "must_have": {{
        "criteria_1_clear_product_type": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_2_key_details": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }}
    }},
    "must_avoid": {{
        "criteria_3_no_extra_details": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_4_no_repetition": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_5_short_and_clear": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_6_no_forbidden_content": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_7_no_brand_only": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }}
    }},
    "must_have_score": 0/1/2,
    "must_avoid_score": 0/1/2,
    "overall_score": 0/1/2,
    "overall_reason": "Overall evaluation reason in English"
}}
"""
        else:
            prompt = f"""You are a professional product title evaluation expert. Please evaluate the optimized title according to the following criteria.

Original Title: {original_title}
Original Description: {original_description}
Optimized Title: {optimized_title}

Evaluation Criteria:

Must Have Requirements:
1. Clear Product Type: The title must include the product type (e.g., "Laptop Lenovo", "Water Bottle") and must match the product type mentioned in the original title and description.
2. Key Details: If there are additional specifications in the original title or description (such as size, material, brand, certificate, application), they should be included in the optimized title.

Must Avoid Issues:
1. No Extra Details: Do not add information not present in the original content.
2. No Repetition or Stuffing: Avoid repeating words or synonym keyword stuffing (e.g., "Steel Metal Bottle Steel").
3. Short and Clear: Title length should be between 3-128 characters (ideal 50-80 characters). Should start with product type, followed by specifications.
4. No Forbidden Content: Do not include prices, VAT, shipping, company names, or incomplete phrases (e.g., ending in "for", "and").
5. No Brand/Model Only: The title cannot be just a brand or model number—must include product type.

Scoring System:
- For "Must Have" criteria: 0=does not meet, 1=partially meets, 2=fully meets
- For "Must Avoid" criteria: 0=problem exists (criterion violated), 1=partial problem, 2=no problem (criterion fully met)

Please score each criterion accordingly and provide detailed evaluation results.

IMPORTANT: All "reason" and "overall_reason" fields must be written in English.

Output format as JSON:
{{
    "must_have": {{
        "criteria_1_clear_product_type": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_2_key_details": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }}
    }},
    "must_avoid": {{
        "criteria_3_no_extra_details": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_4_no_repetition": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_5_short_and_clear": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_6_no_forbidden_content": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_7_no_brand_only": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }}
    }},
    "must_have_score": 0/1/2,
    "must_avoid_score": 0/1/2,
    "overall_score": 0/1/2,
    "overall_reason": "Overall evaluation reason in English"
}}
"""
        
        try:
            system_msg = "You are a professional product content evaluation expert, skilled at objective scoring according to standards. Always provide evaluation reasons in English."
            if source_lang == "de":
                system_msg = "Sie sind ein Experte für die Bewertung von Produktinhalten, der sich auf objektive Bewertung nach Standards versteht. Geben Sie immer Bewertungsgründe auf Englisch an."
            
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ]
            
            response = Generation.call(
                model=self.model,
                messages=messages,
                temperature=0.3,
                result_format='message'
            )
            
            # DashScope API响应处理
            if response.status_code != 200:
                error_msg = getattr(response, 'message', '未知错误')
                raise Exception(f"API调用失败 (状态码: {response.status_code}): {error_msg}")
            
            # 获取响应内容
            if hasattr(response, 'output') and hasattr(response.output, 'choices'):
                result_text = response.output.choices[0].message.content.strip()
            elif hasattr(response, 'output') and hasattr(response.output, 'text'):
                result_text = response.output.text.strip()
            else:
                # 尝试直接访问
                result_text = str(response).strip()
                raise Exception(f"无法解析API响应: {type(response)}")
            
            # 尝试提取JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result
            
        except json.JSONDecodeError as e:
            print(f"评估Title时JSON解析出错: {e}")
            print(f"响应内容: {result_text[:500]}...")
            return {
                "error": f"JSON解析失败: {str(e)}",
                "overall_score": 0
            }
        except Exception as e:
            print(f"评估Title时出错: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "overall_score": 0
            }
    
    def evaluate_description(self, original_title: str, original_description: str,
                            optimized_title: str, optimized_description: str, source_lang: str = "en") -> Dict:
        """评估Description"""
        
        # 判断输入文本长度类别
        original_text_length = len(original_title) + len(original_description)
        if original_text_length < 100:
            length_category = 1  # 输入文本太少
        elif original_text_length < 500:
            length_category = 2  # 输入文本充足
        else:
            length_category = 3  # 输入文本太多
        
        optimized_length = len(optimized_description)
        
        # 根据源语言选择prompt语言
        if source_lang == "de":
            prompt = f"""Sie sind ein Experte für die Bewertung von Produktbeschreibungen. Bitte bewerten Sie die optimierte Beschreibung nach folgenden Kriterien.

Originaltitel: {original_title}
Originalbeschreibung: {original_description}
Optimierter Titel: {optimized_title}
Optimierte Beschreibung: {optimized_description}

Eingabetextlänge-Kategorie: {length_category} (1=zu wenig, 2=ausreichend, 3=zu viel)
Optimierte Beschreibungslänge: {optimized_length} Zeichen

Bewertungskriterien:

Erforderliche Anforderungen (Must Have):
1. Übereinstimmung mit Titel und Original: Die Beschreibung muss die gleichen Details wie der Titel und der Originaltext verwenden, ohne Widersprüche.
2. Wichtige Details zuerst: Der erste Satz sollte den Produkttyp und wichtige Spezifikationen enthalten (falls verfügbar).
3. Klare Struktur: Wenn genügend Informationen vorhanden sind, sollte sie enthalten: Einleitungssatz (Typ + Spezifikationen), Aufzählungspunkte (Funktionen, Materialien usw.), Schlussfolgerung (Wert/Verwendung, falls im Originalinhalt).
4. Angemessene Länge: 
   - Kategorie 1 (Eingabe zu wenig): Ausgabebeschreibung kann <601 Zeichen sein; Fokus auf Klarheit und Genauigkeit
   - Kategorie 2 (Eingabe ausreichend): Ausgabebeschreibung muss >610 Zeichen sein (Ziel 610-700)
   - Kategorie 3 (Eingabe zu viel): Ausgabebeschreibung muss 600-700 Zeichen sein; komprimieren und Redundanz entfernen

Zu vermeidende Probleme (Must Avoid):
1. Keine zusätzlichen Details: Fügen Sie keine Vorteile, Anwendungsfälle, Marketinginformationen oder Spezifikationen hinzu, die nicht im Originalinhalt vorhanden sind.
2. Keine Wiederholung oder Überladung: Vermeiden Sie wiederholte Wörter oder Keyword-Stuffing.
3. Keine verbotenen Inhalte: Enthalten Sie keine Preise, Mehrwertsteuer, Versand, Firmen-/Projektinformationen oder unvollständige Phrasen.
4. Keine Pflegetipps oder Extras: Fügen Sie keine Rezepte, Wartungsratschläge oder nicht unterstützte Behauptungen hinzu.

Bewertungssystem:
- Für "Must Have" Kriterien: 0=erfüllt nicht, 1=teilweise erfüllt, 2=vollständig erfüllt
- Für "Must Avoid" Kriterien: 0=Problem vorhanden (Kriterium verletzt), 1=teilweise Problem, 2=kein Problem (Kriterium vollständig eingehalten)

Bitte bewerten Sie jedes Kriterium entsprechend und geben Sie detaillierte Bewertungsergebnisse.

WICHTIG: Alle "reason" und "overall_reason" Felder müssen auf Englisch geschrieben werden.

Ausgabeformat als JSON:
{{
    "must_have": {{
        "criteria_1_match_title_original": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_2_key_details_upfront": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_3_clear_structure": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_4_proper_length": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }}
    }},
    "must_avoid": {{
        "criteria_5_no_extra_details": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_6_no_repetition": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_7_no_forbidden_content": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_8_no_care_tips": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }}
    }},
    "must_have_score": 0/1/2,
    "must_avoid_score": 0/1/2,
    "overall_score": 0/1/2,
    "overall_reason": "Overall evaluation reason in English"
}}
"""
        else:
            prompt = f"""You are a professional product description evaluation expert. Please evaluate the optimized description according to the following criteria.

Original Title: {original_title}
Original Description: {original_description}
Optimized Title: {optimized_title}
Optimized Description: {optimized_description}

Input Text Length Category: {length_category} (1=too little, 2=sufficient, 3=too much)
Optimized Description Length: {optimized_length} characters

Evaluation Criteria:

Must Have Requirements:
1. Match Title and Original: The description must use the same details as the title and original text, with no contradictions.
2. Key Details Upfront: The first sentence should include product type and key specifications (if available).
3. Clear Structure: If there is enough information, it should include: intro sentence (type + specs), bullet points (features, materials, etc.), conclusion (value/use, if in original content).
4. Proper Length: 
   - Category 1 (input too little): Output description may be <601 characters; focus on clarity and accuracy
   - Category 2 (input sufficient): Output description must be >610 characters (target 610-700)
   - Category 3 (input too much): Output description must be 600-700 characters; condense and remove redundancy

Must Avoid Issues:
1. No Extra Details: Do not add benefits, use cases, marketing information, or specifications not in the original content.
2. No Repetition or Stuffing: Avoid repeating words or keyword stuffing.
3. No Forbidden Content: Do not include prices, VAT, shipping, company/project information, or incomplete phrases.
4. No Care Tips or Extras: Do not add recipes, maintenance advice, or unsupported claims.

Scoring System:
- For "Must Have" criteria: 0=does not meet, 1=partially meets, 2=fully meets
- For "Must Avoid" criteria: 0=problem exists (criterion violated), 1=partial problem, 2=no problem (criterion fully met)

Please score each criterion accordingly and provide detailed evaluation results.

IMPORTANT: All "reason" and "overall_reason" fields must be written in English.

Output format as JSON:
{{
    "must_have": {{
        "criteria_1_match_title_original": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_2_key_details_upfront": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_3_clear_structure": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_4_proper_length": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }}
    }},
    "must_avoid": {{
        "criteria_5_no_extra_details": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_6_no_repetition": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_7_no_forbidden_content": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }},
        "criteria_8_no_care_tips": {{
            "score": 0/1/2,
            "reason": "Evaluation reason in English"
        }}
    }},
    "must_have_score": 0/1/2,
    "must_avoid_score": 0/1/2,
    "overall_score": 0/1/2,
    "overall_reason": "Overall evaluation reason in English"
}}
"""
        
        try:
            system_msg = "You are a professional product content evaluation expert, skilled at objective scoring according to standards. Always provide evaluation reasons in English."
            if source_lang == "de":
                system_msg = "Sie sind ein Experte für die Bewertung von Produktinhalten, der sich auf objektive Bewertung nach Standards versteht. Geben Sie immer Bewertungsgründe auf Englisch an."
            
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ]
            
            response = Generation.call(
                model=self.model,
                messages=messages,
                temperature=0.3,
                result_format='message'
            )
            
            # DashScope API响应处理
            if response.status_code != 200:
                error_msg = getattr(response, 'message', '未知错误')
                raise Exception(f"API调用失败 (状态码: {response.status_code}): {error_msg}")
            
            # 获取响应内容
            if hasattr(response, 'output') and hasattr(response.output, 'choices'):
                result_text = response.output.choices[0].message.content.strip()
            elif hasattr(response, 'output') and hasattr(response.output, 'text'):
                result_text = response.output.text.strip()
            else:
                # 尝试直接访问
                result_text = str(response).strip()
                raise Exception(f"无法解析API响应: {type(response)}")
            
            # 尝试提取JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result
            
        except json.JSONDecodeError as e:
            print(f"评估Description时JSON解析出错: {e}")
            print(f"响应内容: {result_text[:500]}...")
            return {
                "error": f"JSON解析失败: {str(e)}",
                "overall_score": 0
            }
        except Exception as e:
            print(f"评估Description时出错: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "overall_score": 0
            }
    
    def evaluate_product(self, original_title: str, original_description: str,
                        optimized_title: str, optimized_description: str, source_lang: str = "en") -> Dict:
        """评估完整商品内容"""
        
        print(f"正在评估商品: {original_title[:50]}...")
        
        title_result = self.evaluate_title(original_title, original_description, optimized_title, source_lang)
        description_result = self.evaluate_description(
            original_title, original_description, optimized_title, optimized_description, source_lang
        )
        
        # 计算总体评分（兼容新旧格式）
        title_overall = title_result.get("overall_score", 0)
        desc_overall = description_result.get("overall_score", 0)
        
        # 如果新格式存在must_have_score和must_avoid_score，也提取出来
        title_must_have = title_result.get("must_have_score", title_overall)
        title_must_avoid = title_result.get("must_avoid_score", title_overall)
        desc_must_have = description_result.get("must_have_score", desc_overall)
        desc_must_avoid = description_result.get("must_avoid_score", desc_overall)
        
        # 总体评分取平均值（可以调整权重）
        overall_score = round((title_overall + desc_overall) / 2)
        
        return {
            "title_evaluation": title_result,
            "description_evaluation": description_result,
            "overall_score": overall_score,
            "title_score": title_overall,
            "description_score": desc_overall,
            "title_must_have_score": title_must_have,
            "title_must_avoid_score": title_must_avoid,
            "description_must_have_score": desc_must_have,
            "description_must_avoid_score": desc_must_avoid
        }
    
    def evaluate_from_csv(self, input_file: str, output_file: str = None):
        """从CSV文件读取并评估"""
        
        # 确保输入文件路径正确（支持从input文件夹读取）
        if not os.path.isabs(input_file) and not os.path.exists(input_file):
            # 尝试从input文件夹读取
            input_path = os.path.join("input", input_file)
            if os.path.exists(input_path):
                input_file = input_path
        
        if output_file is None:
            # 默认保存到results文件夹
            base_name = os.path.basename(input_file).replace(".csv", "")
            os.makedirs("results", exist_ok=True)
            output_file = os.path.join("results", f"{base_name}_evaluated.csv")
        else:
            # 如果指定了输出文件，确保results文件夹存在
            if not os.path.isabs(output_file):
                os.makedirs("results", exist_ok=True)
                if not output_file.startswith("results/"):
                    output_file = os.path.join("results", output_file)
        
        results = []
        
        with open(input_file, 'r', encoding='utf-8-sig') as f:  # 使用utf-8-sig自动去除BOM
            reader = csv.DictReader(f)
            for row in reader:
                # 支持新的列名
                original_title = row.get('Title_Original', '') or row.get('original_title', '')
                original_description = row.get('Description_original', '') or row.get('original_description', '')
                optimized_title_raw = row.get('Title_AI_optimized', '') or row.get('optimized_title', '')
                optimized_description = row.get('Description_optimized_AI', '') or row.get('optimized_description', '')
                
                if not all([original_title, optimized_title_raw, optimized_description]):
                    print(f"跳过不完整的行")
                    continue
                
                # 解析多个优化后的title（可能是JSON数组格式）
                optimized_titles = []
                try:
                    # 尝试解析为JSON数组
                    if optimized_title_raw.strip().startswith('['):
                        optimized_titles = json.loads(optimized_title_raw)
                    else:
                        # 如果不是JSON，尝试按分隔符分割（如逗号、分号等）
                        optimized_titles = [t.strip() for t in optimized_title_raw.split(',') if t.strip()]
                except:
                    # 如果解析失败，当作单个title处理
                    optimized_titles = [optimized_title_raw]
                
                if not optimized_titles:
                    print(f"跳过：未找到有效的优化title")
                    continue
                
                # 直接使用lang字段的值作为源语言（处理BOM问题）
                lang_field = row.get('lang', '') or row.get('\ufefflang', '')  # 兼容BOM
                lang_field = lang_field.strip().lower()
                if lang_field:
                    # 如果lang字段存在，直接使用其值作为源语言
                    source_lang = lang_field
                    print(f"使用lang字段指定的语言: {source_lang}")
                else:
                    # 如果没有lang字段，则进行自动语言检测
                    title_lang = self.detect_language(original_title)
                    desc_lang = self.detect_language(original_description)
                    
                    # 确定主要语言（优先使用title的语言）
                    source_lang = title_lang if title_lang != "en" else (desc_lang if desc_lang != "en" else "en")
                    
                    print(f"未找到lang字段，自动检测语言 - Title: {title_lang}, Description: {desc_lang}, 使用源语言: {source_lang}")
                
                # 如果有多个优化后的title，分别评估并选择最佳
                if len(optimized_titles) > 1:
                    print(f"发现 {len(optimized_titles)} 个优化后的title，开始分别评估...")
                    best_evaluation = None
                    best_title = None
                    best_score = -1
                    
                    for idx, opt_title in enumerate(optimized_titles, 1):
                        print(f"  评估第 {idx}/{len(optimized_titles)} 个title: {opt_title[:60]}...")
                        evaluation = self.evaluate_product(
                            original_title, original_description,
                            opt_title, optimized_description,
                            source_lang=source_lang
                        )
                        
                        # 计算综合评分（用于比较）
                        title_score = evaluation.get('title_score', 0)
                        desc_score = evaluation.get('description_score', 0)
                        overall_score = evaluation.get('overall_score', 0)
                        # 使用综合评分作为选择标准
                        total_score = title_score + desc_score + overall_score
                        
                        if total_score > best_score:
                            best_score = total_score
                            best_evaluation = evaluation
                            best_title = opt_title
                    
                    print(f"  最佳title: {best_title[:60]}... (评分: {best_evaluation.get('overall_score', 0)}/2)")
                    evaluation = best_evaluation
                    optimized_title = best_title
                else:
                    # 只有一个title，直接评估
                    optimized_title = optimized_titles[0]
                    evaluation = self.evaluate_product(
                        original_title, original_description,
                        optimized_title, optimized_description,
                        source_lang=source_lang
                    )
                
                # 注意：prompt已经要求AI返回英文reason，不需要翻译
                
                # 保存结果（不翻译原始内容，只保留原始内容）
                result_row = {
                    **row,
                    'Title_AI_optimized': optimized_title,  # 保存最佳title
                    'title_score': evaluation['title_score'],
                    'description_score': evaluation['description_score'],
                    'overall_score': evaluation['overall_score'],
                    'title_must_have_score': evaluation.get('title_must_have_score', evaluation['title_score']),
                    'title_must_avoid_score': evaluation.get('title_must_avoid_score', evaluation['title_score']),
                    'description_must_have_score': evaluation.get('description_must_have_score', evaluation['description_score']),
                    'description_must_avoid_score': evaluation.get('description_must_avoid_score', evaluation['description_score']),
                    'title_evaluation': json.dumps(evaluation['title_evaluation'], ensure_ascii=False),
                    'description_evaluation': json.dumps(evaluation['description_evaluation'], ensure_ascii=False),
                    'candidates_count': len(optimized_titles)  # 记录候选title数量
                }
                
                results.append(result_row)
        
        # 保存结果
        if results:
            fieldnames = list(results[0].keys())
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            print(f"\n评估完成！结果已保存到: {output_file}")
            print(f"共评估 {len(results)} 个商品")
            
            # 打印统计信息
            avg_title = sum(r['title_score'] for r in results) / len(results)
            avg_desc = sum(r['description_score'] for r in results) / len(results)
            avg_overall = sum(r['overall_score'] for r in results) / len(results)
            
            print(f"\n平均评分:")
            print(f"  Title: {avg_title:.2f}/2.0")
            print(f"  Description: {avg_desc:.2f}/2.0")
            print(f"  Overall: {avg_overall:.2f}/2.0")
        
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='商品内容AI评估工具')
    parser.add_argument('input_file', help='输入CSV文件路径')
    parser.add_argument('-o', '--output', help='输出CSV文件路径（可选）')
    parser.add_argument('--api-key', help='Qwen/DashScope API Key（可选，也可通过环境变量QWEN_API_KEY或DASHSCOPE_API_KEY设置）')
    parser.add_argument('--model', default='qwen-plus', help='使用的模型名称（默认: qwen-plus，可选: qwen-turbo, qwen-max等）')
    
    args = parser.parse_args()
    
    # 检查API Key
    api_key = args.api_key or os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("错误: 请设置QWEN_API_KEY或DASHSCOPE_API_KEY环境变量或使用--api-key参数")
        return
    
    # 创建评估器并执行评估
    evaluator = ProductContentEvaluator(api_key=api_key, model=args.model)
    evaluator.evaluate_from_csv(args.input_file, args.output)


if __name__ == "__main__":
    main()
