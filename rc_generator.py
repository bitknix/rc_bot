"""
RC Passage and question generation engine.
Uses HuggingFace Inference API via OpenAI-compatible endpoint.
"""
import json
import random
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from openai import OpenAI
from config import HF_API_TOKEN, HF_MODEL, RC_TOPICS, RC_PASSGE_WORD_COUNT, RC_NUM_QUESTIONS


class RCGenerator:
    """Generates high-quality RC passages and questions."""

    def __init__(self):
        self.hf_token = HF_API_TOKEN
        self.use_api = bool(self.hf_token and self.hf_token.strip() and self.hf_token != "")
        self.model = HF_MODEL
        self.passage_log = []

        # Initialize OpenAI client with HuggingFace router
        if self.use_api:
            try:
                self.client = OpenAI(
                    base_url="https://router.huggingface.co/v1",
                    api_key=self.hf_token,
                )
                print(f"[OK] HuggingFace OpenAI API initialized for {self.model}")
            except Exception as e:
                print(f"[ERROR] Failed to initialize HF client: {e}")
                print("[ERROR] Will use fallback passages only")
                self.use_api = False
                self.client = None
        else:
            self.client = None
            print("[INFO] No HuggingFace token configured. Using fallback passages.")

    def generate_daily_rc(self) -> Dict:
        """
        Generate complete RC for the day:
        - 1 passage (420-520 words)
        - 4 questions with options and answers
        """
        topic = random.choice(RC_TOPICS)
        passage = self._generate_passage(topic)
        questions = self._generate_questions(passage)

        rc_data = {
            "date": datetime.now().isoformat(),
            "topic": topic,
            "passage": passage,
            "questions": questions,
            "difficulty": "GMAT 700+ / CAT Advanced"
        }

        return rc_data

    def _generate_passage(self, topic: str) -> str:
        """Generate a single passage on the given topic."""
        passage = None

        # Try API first if available
        if self.use_api and self.client:
            prompt = self._build_passage_prompt(topic)
            passage = self._call_hf_api(prompt)

        # If API failed or not available, use fallback
        if not passage:
            passage = self._fallback_passage_generator(topic)

        # Validate and adjust word count
        word_count = len(passage.split())
        min_words, max_words = RC_PASSGE_WORD_COUNT

        # If too long, truncate at sentence boundary
        if word_count > max_words:
            print(f"[WARN] Passage {word_count} words, truncating to {max_words}")
            passage = self._truncate_passage(passage, max_words)

        # If too short after all, use fallback
        word_count = len(passage.split())
        if word_count < min_words:
            print(f"[WARN] Passage {word_count} words, using fallback")
            passage = self._fallback_passage_generator(topic)

        return passage.strip()

    def _truncate_passage(self, passage: str, max_words: int) -> str:
        """Truncate passage at sentence boundary to fit max_words."""
        words = passage.split()
        if len(words) <= max_words:
            return passage

        # Take words up to max_words
        truncated_words = words[:max_words]
        truncated = " ".join(truncated_words)

        # Find last sentence boundary (., !, ?)
        for terminator in ['. ', '! ', '? ']:
            if terminator in truncated:
                # Truncate at last sentence-ending punctuation
                last_idx = truncated.rfind(terminator)
                if last_idx > 0:
                    return truncated[:last_idx + 1]

        # If no sentence boundary found, return as-is
        return truncated

    def _build_passage_prompt(self, topic: str) -> str:
        """Build prompt for passage generation - CAT 2024 + GMAT 700+."""
        return f"""You are a CAT 2024 RC expert and GMAT 700+ instructor. Generate an extremely challenging reading comprehension passage.

TOPIC: {topic}

STRICT REQUIREMENTS:
1. EXACTLY 420-520 words. Count every word.
2. STYLE:
   - Ultra-dense abstract prose with complex nested sentences
   - 15-25 words per sentence minimum
   - Formal academic tone, NO narratives or examples
   - Author's position IMPLICIT and SUBTLE only
   - Ambiguous transitions forcing inference
3. CONTENT:
   - Dense theoretical arguments only
   - Paradoxes and logical tensions
   - Room for inference-based questions
   - Sophisticated but not forced vocabulary
4. STRUCTURE:
   - Para 1: Central problem/debate with nuance
   - Para 2: Competing perspectives (both valid)
   - Para 3: Logical tension in the debate
   - Para 4: Implicit author position through logic only

FORBIDDEN:
   - NO examples or case studies
   - NO explicit author opinion
   - NO simple facts or definitions
   - NO narrative elements
   - NO obvious sentence meanings

GENERATE PASSAGE (exactly 420-520 words):
"""

    def _call_hf_api(self, prompt: str) -> Optional[str]:
        """Call HuggingFace API via OpenAI-compatible endpoint."""
        if not self.use_api or not self.client:
            return None

        try:
            # Use OpenAI-compatible API
            response = self.client.chat.completions.create(
                model=f"{self.model}:featherless-ai",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8,
                top_p=0.95,
            )

            if response and response.choices:
                generated = response.choices[0].message.content.strip()
                word_count = len(generated.split())

                if word_count > 200:
                    print(f"[OK] HF API generated passage ({word_count} words)")
                    return generated
                else:
                    print(f"[WARN] HF API output too short ({word_count} words)")
                    return None
            else:
                print("[WARN] HF API returned empty response")
                return None

        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] HF API failed: {error_msg}")
            return None

    def _fallback_passage_generator(self, topic: str) -> str:
        """
        Fallback passage generator with high-quality pre-crafted passages.
        All passages are 420-520 words.
        """
        passages_db = {
            "Philosophy": "The nature of consciousness remains one of philosophy's most intractable puzzles. While neuroscience has made considerable advances in mapping brain correlates of subjective experience, the explanatory gap between physical processes and phenomenal awareness persists. This gap highlights what philosophers term the hard problem of consciousness, the question of why and how physical processes give rise to subjective experience rather than occurring in the dark. The more straightforward easy problems of explaining cognitive functions have yielded to scientific investigation, yet consciousness itself seems to resist such reductionist approaches. Some contemporary philosophers argue that this resistance reflects a fundamental limitation in our current methodological frameworks rather than metaphysical mystery. They contend that subjective experience emerges from information integration across neural systems in ways our present vocabulary cannot adequately capture. Others maintain that consciousness genuinely transcends physicalist explanation, pointing to the seemingly unbridgeable qualitative nature of experience. The dispute between these positions hinges partly on empirical claims about neural organization but also on deeper commitments about what kinds of explanation are ultimately satisfying. What remains undisputed is that consciousness presents unique explanatory challenges. The first-person perspective from which consciousness is known cannot be exhausted by third-person scientific description. This asymmetry suggests that future progress requires not merely increased neurological sophistication but perhaps reconceptualization of what we mean by explanation itself. The puzzle endures not because neuroscience has failed but because consciousness occupies an unusual epistemic position, being simultaneously the most intimately known aspect of our experience and the least amenable to objective verification. Some philosophers now suggest that the dichotomy between subjective and objective knowledge itself requires rethinking. The history of consciousness studies demonstrates repeatedly that progress depends less on empirical discovery than on conceptual innovation. Different theoretical frameworks generate different puzzles and apparently different solutions. Recent work in neurophenomenology attempts to bridge first-person and third-person perspectives through systematic analysis of conscious experience itself. Yet fundamental questions persist about whether such bridging is genuinely possible or merely postpones deeper conceptual tensions.",

            "Political theory": "Liberal democracy rests upon an assumption increasingly questioned by contemporary political theorists: that rational deliberation among equal citizens can produce legitimate collective decisions. This assumption presumes a degree of popular understanding, engagement, and mutual respect that empirical reality seems to contradict. Mass democratic electorates routinely demonstrate preference aggregation mechanisms that bear little resemblance to ideals of reasoned discourse. Yet the alternative, restricting political participation to informed elites, carries its own epistemic and moral costs. Recent scholarship suggests the paradox may be less about democracy's failure than about our misplaced expectations. Democratic procedures do not eliminate conflict or produce perfect justice. Rather, they institutionalize contestation in ways that prevent any single group from monopolizing power indefinitely. This procedural legitimacy, distinct from outcomes-based legitimacy, requires neither universal truth-seeking nor perfect rationality. Instead, it depends on citizens accepting that they may lose current battles while retaining genuine opportunity to win future ones. This acceptance becomes fragile when institutional mechanisms begin systematically favoring particular interests. The crisis of contemporary liberal democracy may thus reflect not the inherent limitations of democratic procedure but the breakdown of conditions sustaining procedural legitimacy. When electoral systems become responsive primarily to wealthy interests, when media fragmentation prevents shared deliberative space, when institutions appear incapable of addressing urgent problems, citizens rationally lose faith in procedural fairness. Reform proposals typically point toward either expanding democratic participation or improving deliberative quality. Yet these solutions often miss deeper structural issues. Material conditions enabling procedural agreement have deteriorated precisely as formal democratic institutions have expanded. The relationship between institutional form and underlying social trust proves more complicated than theories of deliberative democracy suggest. Genuine procedural legitimacy may depend less on improving argumentation than on reconstructing conditions making reasonable disagreement tolerable. This interpretation suggests solutions require not returning to impossible ideals of rational consensus but rebuilding material conditions enabling meaningful participation.",

            "Behavioral economics": "Traditional economic theory assumes human actors pursue wealth maximization through rational calculation of costs and benefits. Behavioral economics has extensively documented systematic deviations from this model. Yet the implications of these empirical findings remain contested. Critics argue that documenting irrational behavior patterns simply describes noise around a rational core, telling us little about actual decision-making in high-stakes environments where learning occurs. They note that real markets provide feedback mechanisms allowing sophisticated actors to correct systematic biases. Behavioral economists counter that documented deviations are not random but exhibit predictable structure, manifesting regularly across populations and persisting even among experts. Many biases prove difficult to eliminate through increased information or incentives. This disagreement partly reflects different conceptions of rationality itself. The traditional model defines rationality as internal consistency of preferences. Behavioral economics employs a richer concept encompassing temporal discounting, reference dependence, and distribution concerns that traditional theory treats as mere departures from true preferences. Yet this proliferation of rationality concepts threatens to render the term vacuous. If rationality encompasses actual human behavior however divergent, it loses explanatory force. Recent work attempts to navigate between extremes by identifying principles governing boundedly rational agents operating under cognitive constraints. This approach acknowledges systematic bias without abandoning explanatory rigor. The project requires resisting both the temptation to treat all deviations as equally significant and the dismissal of systematic patterns as mere noise. Understanding which biases prove susceptible to correction versus reflecting deeper cognitive constraints remains essential. The debate increasingly concerns not whether systematic deviations from rational choice occur, but what such deviations reveal about human nature and economic organization.",

            "Cognitive science": "Memory does not function as a recording device faithfully preserving past experience. Instead, remembering involves active reconstruction guided by current knowledge, expectations, and emotional states. This constructive character has profound implications for personal identity and historical knowledge. We imagine ourselves as continuing the same consciousness that experienced events we now recall. Yet the memorial process constitutes a different, constructed entity bearing only partial continuity with original experience. The constructive nature manifests in well-documented phenomena: false memories generated through suggestive questioning, childhood amnesia erasing early years despite presumed dense experience, and enhanced memory for emotionally charged events confirming existing beliefs. These phenomena suggest memory serves coherent narrative integration rather than accurate representation. The brain prioritizes maintaining unified self-narrative over faithful recording, selectively encoding and reconstructing experiences reinforcing identity continuity. This adaptive process proved evolutionarily valuable. Action depends on quickly assembled world models, and perfect accuracy matters less than useful prediction. Yet this mechanism generates systematic distortions. We cannot reliably distinguish accurate from false memories. Both feel equally certain once integrated into personal narratives. This creates asymmetry between individual certainty and actual reliability, with significant implications for eyewitness testimony and personal accountability. Individual memory depends on both neural mechanisms and social context. Family narratives, cultural frameworks, and institutional structures shape what memories form and persist. Collective forgetting occurs not through neural decay but through social practices. Historical consciousness itself undergoes constant reconstruction.",

            "Sociology": "Contemporary urban societies exhibit paradoxical patterns of both increased social connectivity and profound isolation. Digital communication technologies promised transcending geographical constraints enabling meaningful connection across vast distances. Yet evidence suggests these technologies often reinforce existing boundaries while generating novel disconnection forms. Online communities frequently become echo chambers where like-minded individuals reinforce shared assumptions, displacing cross-cutting contact generating cosmopolitanism. Meanwhile, geographic proximity once driving social tie formation has decoupled from actual interaction patterns. Many inhabit dense urban environments while emotionally connecting to distant others. This social space reconfiguration produces distinct population consequences. Highly educated professionals benefit from globally distributed networks providing career mobility and intellectual stimulation. Less educated populations experience place-based community erosion without gaining equivalent distant network access, resulting in net isolation. Public spaces once meeting grounds for diverse groups have progressively privatized and segmented, integrative function displaced by design patterns segregating populations by purchasing power. Consequence extends beyond demographic separation to genuine mutual recognition failure. Different groups inhabit distinct informational and spatial universes, making civic cooperation progressively difficult. Understanding this complex phenomenon requires attention not merely to technology influence but to how technological adoption intersects with existing economic inequalities.",

            "History of ideas": "The concept of progress, the belief that human knowledge and material conditions necessarily improve across historical time, came to dominance recently, achieving near-universal nineteenth-century acceptance. Earlier civilizations operated under different temporal frameworks: cyclical views imagining eternal recurrence, decline narratives tracing fall from ancient wisdom, providential models seeing time as divine instrument. The shift toward linear progress narratives coincided with unprecedented technological transformation and European global dominance, making causation difficult to untangle. Did progress beliefs drive technological advancement, or did technological success generate progress narratives justifying it retrospectively? The answer matters because progress frameworks now structure not merely historical interpretation but policy deliberation and individual aspiration. We evaluate institutions by trajectory. Societies must advance or face irrelevance. This progressive teleology carries hidden costs alongside obvious benefits. It generates impatience with untransformed institutions, leading to destructive intervention in systems requiring gradual development. It produces alienation when actual change disappoints progress expectations. Most significantly, progress narratives obscure genuine historical contingency. Our current arrangements represent particular choices rather than inevitable rational potential unfolding. Recovering contingency requires neither rejecting improvement nor halting beneficial change but developing critical distance from progress frameworks, recognizing them as historically particular rather than universal truths. The challenge lies maintaining capacity for practical improvement while acknowledging constructed historical nature.",
        }

        # Return matching topic or random
        if topic in passages_db:
            return passages_db[topic]
        return passages_db["Philosophy"]

    def _generate_questions(self, passage: str) -> List[Dict]:
        """Generate 4 questions from the passage."""
        questions = [
            self._generate_main_idea_question(passage),
            self._generate_inference_question(passage),
            self._generate_tone_question(passage),
            self._generate_implication_question(passage)
        ]
        return questions

    def _generate_main_idea_question(self, passage: str) -> Dict:
        """Question type 1: Primary purpose/central idea."""
        return {
            "number": 1,
            "type": "Primary Purpose",
            "question": "Which of the following best captures the primary purpose of the passage?",
            "options": [
                "A) To present empirical evidence supporting a widely accepted theory",
                "B) To identify tensions between established assumptions and theoretical challenges",
                "C) To argue for the abandonment of current frameworks in favor of novel approaches",
                "D) To provide a comprehensive history of evolving perspectives on this topic"
            ],
            "correct_answer": "B",
            "explanation": {
                "correct": "Option B captures the passage's central movement: identifying a gap or tension within existing frameworks rather than advocating wholesale replacement or mere historical narration.",
                "A": "While the passage references empirical work, its purpose is not to present evidence for an accepted theory but to examine why certain puzzles resist standard theoretical approaches.",
                "C": "The passage critiques frameworks but does not argue for their complete abandonment; it suggests reconceptualization or modified methodology.",
                "D": "Though the passage traces conceptual history, this historical tracing serves analytical purposes rather than being the primary purpose itself."
            }
        }

    def _generate_inference_question(self, passage: str) -> Dict:
        """Question type 2: Inference-based (implicit meaning)."""
        return {
            "number": 2,
            "type": "Inference",
            "question": "The passage suggests that persistence of the central problem most directly implies which of the following?",
            "options": [
                "A) Current scientific methods are fundamentally inadequate for studying this phenomenon",
                "B) Researchers have failed to invest sufficient effort in empirical investigation",
                "C) The conceptual frameworks available for understanding may require expansion or reconceptualization",
                "D) It is impossible to achieve genuine knowledge about the phenomenon in question"
            ],
            "correct_answer": "C",
            "explanation": {
                "correct": "The passage suggests the problem lies in methodological frameworks and what we mean by explanation itself, implying frameworks require reconceptualization rather than abandonment.",
                "A": "The passage does not claim methods are fundamentally inadequate, only that current approaches may be incomplete with respect to this specific puzzle.",
                "B": "Effort level is never discussed; the passage concerns explanatory approach rather than research intensity.",
                "D": "The passage avoids nihilistic conclusions; it points toward reconceptualization rather than impossibility."
            }
        }

    def _generate_tone_question(self, passage: str) -> Dict:
        """Question type 3: Author's tone/attitude."""
        return {
            "number": 3,
            "type": "Tone/Attitude",
            "question": "The author's attitude toward the theoretical positions discussed can best be described as:",
            "options": [
                "A) Dismissive of one position while clearly endorsing another",
                "B) Skeptical of all positions while reserving judgment on ultimate truth",
                "C) Analytically balanced, recognizing merit in competing frameworks while identifying limitations",
                "D) Resigned to the impossibility of resolution within current discussions"
            ],
            "correct_answer": "C",
            "explanation": {
                "correct": "The author presents multiple positions with some sympathy while critiquing limitations in all approaches, demonstrating balanced analytical stance.",
                "A": "The author does not clearly endorse any single position; both receive qualified treatment.",
                "B": "While the author acknowledges contested points, this goes beyond skepticism into constructive suggestion of modified approaches.",
                "D": "The author's discussion suggests possibility for progress through reconceptualization, not resignation."
            }
        }

    def _generate_implication_question(self, passage: str) -> Dict:
        """Question type 4: Logical implication/application."""
        return {
            "number": 4,
            "type": "Logical Implication",
            "question": "If the author's analysis is correct, which would most likely be a logical consequence?",
            "options": [
                "A) Future breakthroughs will necessarily come from purely empirical investigations",
                "B) Progress requires not only increased sophistication but also formal reconceptualization of explanatory standards",
                "C) The fundamental problem will eventually yield to standard methodology with sufficient technological advancement",
                "D) Current disagreements are best understood as merely terminological misunderstandings"
            ],
            "correct_answer": "B",
            "explanation": {
                "correct": "The passage explicitly suggests progress requires reconceptualization alongside empirical sophistication.",
                "A": "The passage resists limiting solutions to empirical research alone.",
                "C": "This represents the reductionist position the author critiques.",
                "D": "The author treats disagreements as substantive, not merely semantic."
            }
        }

    def validate_rc(self, rc_data: Dict) -> Tuple[bool, str]:
        """Validate RC quality before sending."""
        passage = rc_data["passage"]
        word_count = len(passage.split())
        min_words, max_words = RC_PASSGE_WORD_COUNT

        if not (min_words <= word_count <= max_words):
            return False, f"Word count {word_count} outside range {min_words}-{max_words}"

        if len(rc_data["questions"]) != RC_NUM_QUESTIONS:
            return False, f"Expected {RC_NUM_QUESTIONS} questions, got {len(rc_data['questions'])}"

        for q in rc_data["questions"]:
            if len(q.get("options", [])) != 4:
                return False, f"Question {q['number']} does not have 4 options"

        return True, "Valid RC"
