"""
Company Brand Profile Management
Handles brand customization, questionnaires, and style generation
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class DesignStyle(Enum):
    MODERN_CORPORATE = "modern_corporate"
    STARTUP_VIBRANT = "startup_vibrant"
    PROFESSIONAL_CLASSIC = "professional_classic"
    CREATIVE_MINIMAL = "creative_minimal"

@dataclass
class ColorPalette:
    """Color palette configuration"""
    primary: List[str] = None
    secondary: List[str] = None
    accent: str = ""
    background: str = "#FFFFFF"
    text: str = "#000000"
    text_light: str = "#666666"

    def __post_init__(self):
        if self.primary is None:
            self.primary = ["#1976D2", "#2196F3"]
        if self.secondary is None:
            self.secondary = ["#424242", "#757575"]

@dataclass
class Typography:
    """Typography configuration"""
    heading_font: str = "Inter"
    body_font: str = "Inter"
    monospace_font: str = "Fira Code"
    heading_sizes: Dict[str, int] = None
    line_height: float = 1.5
    letter_spacing: float = 0.0

    def __post_init__(self):
        if self.heading_sizes is None:
            self.heading_sizes = {
                "h1": 48,
                "h2": 36,
                "h3": 28,
                "h4": 22,
                "h5": 18,
                "h6": 16
            }

@dataclass
class Layout:
    """Layout configuration"""
    max_width: int = 1200
    margins: Dict[str, int] = None
    padding: Dict[str, int] = None
    spacing: Dict[str, int] = None

    def __post_init__(self):
        if self.margins is None:
            self.margins = {"top": 60, "bottom": 60, "left": 40, "right": 40}
        if self.padding is None:
            self.padding = {"section": 40, "element": 20}
        if self.spacing is None:
            self.spacing = {"small": 8, "medium": 16, "large": 24, "xlarge": 32}

@dataclass
class BrandAssets:
    """Brand assets configuration"""
    logo_path: Optional[str] = None
    logo_size: Dict[str, int] = None
    favicon_path: Optional[str] = None
    background_image: Optional[str] = None

    def __post_init__(self):
        if self.logo_size is None:
            self.logo_size = {"width": 200, "height": 60}

@dataclass
class BrandProfile:
    """Complete brand profile for a company"""
    company_name: str
    industry: str
    tagline: str = ""
    website: str = ""
    design_style: DesignStyle = DesignStyle.MODERN_CORPORATE
    color_palette: ColorPalette = None
    typography: Typography = None
    layout: Layout = None
    brand_assets: BrandAssets = None
    preferences: Dict[str, Any] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if self.color_palette is None:
            self.color_palette = ColorPalette()
        if self.typography is None:
            self.typography = Typography()
        if self.layout is None:
            self.layout = Layout()
        if self.brand_assets is None:
            self.brand_assets = BrandAssets()
        if self.preferences is None:
            self.preferences = {}

class BrandQuestionnaire:
    """Interactive questionnaire for creating brand profiles"""

    def __init__(self, config=None):
        self.config = config
        self.questions = self._load_questions()

    def _load_questions(self) -> List[Dict]:
        """Load questionnaire questions"""

        return [
            {
                "id": "company_name",
                "question": "What is your company name?",
                "type": "text",
                "required": True,
                "validation": "no_special_chars"
            },
            {
                "id": "industry",
                "question": "What industry is your company in?",
                "type": "select",
                "options": [
                    "Agritech", "Telecom", "SaaS", "Finance", "Healthcare",
                    "Retail", "Manufacturing", "Education", "Energy", "Other"
                ],
                "required": True
            },
            {
                "id": "tagline",
                "question": "What is your company tagline or slogan?",
                "type": "text",
                "required": False
            },
            {
                "id": "website",
                "question": "What is your company website?",
                "type": "url",
                "required": False
            },
            {
                "id": "design_preference",
                "question": "How would you describe your desired design style?",
                "type": "single_choice",
                "options": [
                    "Modern and professional - Clean, corporate look with blue/neutral colors",
                    "Bold and vibrant - Energetic, startup feel with bright colors",
                    "Traditional and established - Conservative, trustworthy appearance",
                    "Minimalist and creative - Clean, white-space focused design"
                ],
                "required": True,
                "mapping": {
                    "Modern and professional - Clean, corporate look with blue/neutral colors": DesignStyle.MODERN_CORPORATE,
                    "Bold and vibrant - Energetic, startup feel with bright colors": DesignStyle.STARTUP_VIBRANT,
                    "Traditional and established - Conservative, trustworthy appearance": DesignStyle.PROFESSIONAL_CLASSIC,
                    "Minimalist and creative - Clean, white-space focused design": DesignStyle.CREATIVE_MINIMAL
                }
            },
            {
                "id": "color_preference",
                "question": "Do you have specific color preferences?",
                "type": "multi_choice",
                "options": [
                    "Blue tones (professional, trustworthy)",
                    "Green tones (growth, natural, eco-friendly)",
                    "Purple/Indigo (innovative, creative)",
                    "Red/Orange (energetic, bold)",
                    "Neutral grays (conservative, clean)",
                    "I'll use industry-standard colors"
                ],
                "required": False
            },
            {
                "id": "typography_preference",
                "question": "What typography style do you prefer?",
                "type": "single_choice",
                "options": [
                    "Modern sans-serif (clean, digital-first)",
                    "Traditional serif (established, literary)",
                    "Technical fonts (precise, data-focused)",
                    "Creative fonts (unique, brand-focused)",
                    "I'll use industry-standard fonts"
                ],
                "required": False
            },
            {
                "id": "brand_personality",
                "question": "Select 3 words that describe your brand personality:",
                "type": "multi_choice",
                "max_choices": 3,
                "options": [
                    "Innovative", "Professional", "Approachable", "Bold", "Trustworthy",
                    "Creative", "Efficient", "Luxury", "Eco-friendly", "Tech-focused",
                    "Traditional", "Modern", "Friendly", "Authoritative", "Playful"
                ],
                "required": True
            },
            {
                "id": "target_audience",
                "question": "Who is your primary target audience?",
                "type": "select",
                "options": [
                    "Enterprise/B2B clients",
                    "Small to medium businesses",
                    "Individual consumers",
                    "Investors and stakeholders",
                    "Government/Institutional",
                    "Multiple audiences"
                ],
                "required": True
            },
            {
                "id": "logo_upload",
                "question": "Do you have a company logo you'd like to use?",
                "type": "file",
                "accept": ".png,.jpg,.jpeg,.svg",
                "required": False
            }
        ]

    def run_interactive(self) -> BrandProfile:
        """Run interactive questionnaire and return brand profile"""
        print("\n" + "="*60)
        print("🎨 BRAND PROFILE QUESTIONNAIRE")
        print("="*60)
        print("Let's create a beautiful brand profile for your documents!\n")

        answers = {}

        for question in self.questions:
            answer = self._ask_question(question)
            if answer is not None:
                answers[question["id"]] = answer

        return self._create_brand_profile(answers)

    def _ask_question(self, question: Dict) -> Any:
        """Ask a single question and get answer"""

        question_text = f"❓ {question['question']}"
        if question.get("required"):
            question_text += " (Required)"

        print(f"\n{question_text}")

        if question["type"] == "text":
            return input("Your answer: ").strip()

        elif question["type"] == "url":
            while True:
                url = input("URL (or press Enter to skip): ").strip()
                if not url:
                    return None
                if url.startswith(('http://', 'https://')):
                    return url
                print("Please enter a valid URL starting with http:// or https://")

        elif question["type"] == "select":
            options = question["options"]
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")

            while True:
                try:
                    choice = input(f"Select 1-{len(options)}: ").strip()
                    index = int(choice) - 1
                    if 0 <= index < len(options):
                        return options[index]
                except ValueError:
                    pass
                print("Please enter a valid number")

        elif question["type"] == "single_choice":
            options = question["options"]
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")

            while True:
                try:
                    choice = input(f"Select 1-{len(options)}: ").strip()
                    index = int(choice) - 1
                    if 0 <= index < len(options):
                        selected = options[index]
                        if "mapping" in question:
                            return question["mapping"][selected]
                        return selected
                except ValueError:
                    pass
                print("Please enter a valid number")

        elif question["type"] == "multi_choice":
            options = question["options"]
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")

            max_choices = question.get("max_choices", len(options))
            choices = []

            while len(choices) < max_choices:
                try:
                    choice = input(f"Select options (1-{len(options)}) or press Enter to finish: ").strip()
                    if not choice:
                        break
                    index = int(choice) - 1
                    if 0 <= index < len(options):
                        if options[index] not in choices:
                            choices.append(options[index])
                        else:
                            print("Already selected")
                    else:
                        print("Please enter a valid number")
                except ValueError:
                    print("Please enter a valid number")

            return choices if choices else None

        elif question["type"] == "file":
            path = input("File path (or press Enter to skip): ").strip()
            if path and Path(path).exists():
                return path
            return None

        return None

    def _create_brand_profile(self, answers: Dict) -> BrandProfile:
        """Create brand profile from questionnaire answers"""

        company_name = answers.get("company_name", "Untitled Company")
        industry = answers.get("industry", "Technology").lower()

        profile = BrandProfile(
            company_name=company_name,
            industry=industry,
            tagline=answers.get("tagline", ""),
            website=answers.get("website", ""),
            design_style=answers.get("design_preference", DesignStyle.MODERN_CORPORATE)
        )

        # Customize color palette based on preferences
        color_preferences = answers.get("color_preference", [])
        if color_preferences and isinstance(color_preferences, list):
            profile.color_palette = self._generate_color_palette(
                industry, color_preferences, profile.design_style
            )

        # Customize typography based on preferences
        typo_preference = answers.get("typography_preference")
        if typo_preference:
            profile.typography = self._generate_typography(
                typo_preference, profile.design_style
            )

        # Store brand personality
        brand_personality = answers.get("brand_personality", [])
        if brand_personality:
            profile.preferences["brand_personality"] = brand_personality

        # Store target audience
        target_audience = answers.get("target_audience", "")
        if target_audience:
            profile.preferences["target_audience"] = target_audience

        # Handle logo
        logo_path = answers.get("logo_upload")
        if logo_path:
            profile.brand_assets.logo_path = logo_path

        return profile

    def _generate_color_palette(self, industry: str, preferences: List[str], style: DesignStyle) -> ColorPalette:
        """Generate color palette based on industry and preferences"""

        industry_colors = {
            "agritech": ["#4CAF50", "#2E7D32", "#8BC34A", "#689F38"],
            "telecom": ["#1976D2", "#0D47A1", "#2196F3", "#64B5F6"],
            "saas": ["#6200EA", "#7C4DFF", "#9C27B0", "#BA68C8"],
            "finance": ["#388E3C", "#1B5E20", "#4CAF50", "#81C784"],
            "healthcare": ["#00838F", "#006064", "#00ACC1", "#26C6DA"],
            "retail": ["#F44336", "#C62828", "#E91E63", "#EC407A"]
        }

        color_mapping = {
            "Blue tones (professional, trustworthy)": ["#1976D2", "#2196F3", "#42A5F5", "#64B5F6"],
            "Green tones (growth, natural, eco-friendly)": ["#4CAF50", "#66BB6A", "#81C784", "#A5D6A7"],
            "Purple/Indigo (innovative, creative)": ["#673AB7", "#7E57C2", "#9575CD", "#B39DDB"],
            "Red/Orange (energetic, bold)": ["#F44336", "#FF5722", "#FF7043", "#FF8A65"],
            "Neutral grays (conservative, clean)": ["#424242", "#616161", "#757575", "#9E9E9E"]
        }

        if "I'll use industry-standard colors" in preferences:
            primary_colors = industry_colors.get(industry, industry_colors["saas"])
        else:
            primary_colors = []
            for pref in preferences:
                if pref in color_mapping:
                    primary_colors.extend(color_mapping[pref])

            if not primary_colors:
                primary_colors = industry_colors.get(industry, industry_colors["saas"])

        palette = ColorPalette(
            primary=primary_colors[:3] if len(primary_colors) >= 3 else primary_colors,
            secondary=["#424242", "#757575", "#BDBDBD"],
            accent=primary_colors[0] if primary_colors else "#2196F3"
        )

        return palette

    def _generate_typography(self, preference: str, style: DesignStyle) -> Typography:
        """Generate typography configuration based on preference and style"""

        typography_map = {
            "Modern sans-serif (clean, digital-first)": {
                "heading": "Inter",
                "body": "Inter"
            },
            "Traditional serif (established, literary)": {
                "heading": "Georgia",
                "body": "Georgia"
            },
            "Technical fonts (precise, data-focused)": {
                "heading": "Roboto",
                "body": "Roboto"
            },
            "Creative fonts (unique, brand-focused)": {
                "heading": "Montserrat",
                "body": "Montserrat"
            }
        }

        if preference in typography_map:
            fonts = typography_map[preference]
            return Typography(
                heading_font=fonts["heading"],
                body_font=fonts["body"],
                monospace_font="Fira Code"
            )

        # Style-based defaults
        style_fonts = {
            DesignStyle.MODERN_CORPORATE: ("Inter", "Inter"),
            DesignStyle.STARTUP_VIBRANT: ("Montserrat", "Inter"),
            DesignStyle.PROFESSIONAL_CLASSIC: ("Georgia", "Arial"),
            DesignStyle.CREATIVE_MINIMAL: ("Inter", "Inter")
        }

        heading, body = style_fonts.get(style, style_fonts[DesignStyle.MODERN_CORPORATE])
        return Typography(heading_font=heading, body_font=body)

class BrandProfileManager:
    """Manages saving and loading brand profiles"""

    def __init__(self, brand_profiles_dir: Path):
        self.brand_profiles_dir = brand_profiles_dir
        self.brand_profiles_dir.mkdir(exist_ok=True)

    def save_profile(self, profile: BrandProfile) -> str:
        """Save brand profile to file"""

        from datetime import datetime

        profile.updated_at = datetime.now().isoformat()
        if not profile.created_at:
            profile.created_at = profile.updated_at

        filename = f"{profile.company_name.lower().replace(' ', '_')}_brand_profile.json"
        file_path = self.brand_profiles_dir / filename

        # Convert to serializable format
        profile_dict = asdict(profile)
        profile_dict["design_style"] = profile.design_style.value

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(profile_dict, f, indent=2, ensure_ascii=False)

        return str(file_path)

    def load_profile(self, company_name: str) -> Optional[BrandProfile]:
        """Load brand profile for company"""

        filename = f"{company_name.lower().replace(' ', '_')}_brand_profile.json"
        file_path = self.brand_profiles_dir / filename

        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                profile_dict = json.load(f)

            # Convert back to BrandProfile
            profile_dict["design_style"] = DesignStyle(profile_dict["design_style"])
            profile_dict["color_palette"] = ColorPalette(**profile_dict["color_palette"])
            profile_dict["typography"] = Typography(**profile_dict["typography"])
            profile_dict["layout"] = Layout(**profile_dict["layout"])
            profile_dict["brand_assets"] = BrandAssets(**profile_dict["brand_assets"])

            return BrandProfile(**profile_dict)

        except Exception as e:
            print(f"Error loading brand profile: {e}")
            return None

    def list_profiles(self) -> List[str]:
        """List all available company profiles"""

        profiles = []
        for file_path in self.brand_profiles_dir.glob("*_brand_profile.json"):
            company_name = file_path.stem.replace("_brand_profile", "").replace("_", " ").title()
            profiles.append(company_name)

        return profiles