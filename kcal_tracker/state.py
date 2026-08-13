import reflex as rx
import datetime
import re

class State(rx.State):
    """The main application state for Kcal Tracker."""
    
    # Target Goals
    target_calories: int = 2200
    target_protein: int = 160
    target_carbs: int = 220
    target_fat: int = 65

    # Logged Meals
    logged_meals: list[dict] = [
        {
            "id": "m1",
            "name": "Oatmeal with Berries & Whey",
            "category": "Breakfast",
            "calories": 420,
            "protein": 28,
            "carbs": 58,
            "fat": 7,
            "time": "08:30 AM",
        },
        {
            "id": "m2",
            "name": "Grilled Chicken Salad & Quinoa",
            "category": "Lunch",
            "calories": 550,
            "protein": 48,
            "carbs": 45,
            "fat": 14,
            "time": "12:45 PM",
        },
    ]

    # Saved Recipes
    recipes: list[dict] = [
        {
            "id": "r1",
            "name": "High-Protein Salmon & Rice Bowl",
            "ingredients": "180g Salmon fillet, 150g cooked Jasmine rice, 100g steamed broccoli, 10ml soy sauce",
            "servings": 1,
            "calories": 620,
            "protein": 45,
            "carbs": 50,
            "fat": 18,
        },
        {
            "id": "r2",
            "name": "Post-Workout Whey Smoothie",
            "ingredients": "1 scoop Whey Isolate, 1 medium Banana, 250ml Almond Milk, 15g Peanut Butter",
            "servings": 1,
            "calories": 320,
            "protein": 32,
            "carbs": 35,
            "fat": 4,
        },
        {
            "id": "r3",
            "name": "Egg & Avocado Protein Wrap",
            "ingredients": "2 Whole Eggs, 2 Whole Wheat Tortillas, 1/2 Avocado, 30g Low-fat Cheese",
            "servings": 1,
            "calories": 480,
            "protein": 24,
            "carbs": 38,
            "fat": 22,
        },
    ]

    # Chatbot State
    chat_input: str = ""
    chat_history: list[dict] = [
        {
            "id": "c1",
            "sender": "ai",
            "text": "👋 Welcome to your AI Calorie Tracker! I can log your meals, calculate macros, save recipes, and answer nutritional questions.\n\nTry saying: *'Log 2 eggs and toast (350 kcal, 18g protein)'* or *'Create a recipe for Protein Oatmeal'*.",
            "timestamp": "08:00 AM",
            "action": "",
        }
    ]
    is_chat_thinking: bool = False

    # Active view tab on mobile/dashboard ("dashboard" or "chat" or "all")
    active_tab: str = "dashboard"

    # Dialog state for Adding/Editing Meals
    show_meal_modal: bool = False
    is_editing_meal: bool = False
    meal_form_id: str = ""
    meal_form_name: str = ""
    meal_form_category: str = "Lunch"
    meal_form_calories: int = 300
    meal_form_protein: int = 25
    meal_form_carbs: int = 30
    meal_form_fat: int = 10

    # Dialog state for Adding/Editing Recipes
    show_recipe_modal: bool = False
    is_editing_recipe: bool = False
    recipe_form_id: str = ""
    recipe_form_name: str = ""
    recipe_form_ingredients: str = ""
    recipe_form_servings: int = 1
    recipe_form_calories: int = 400
    recipe_form_protein: int = 30
    recipe_form_carbs: int = 40
    recipe_form_fat: int = 12

    # Dialog state for Target Goals
    show_target_modal: bool = False
    target_form_calories: int = 2200
    target_form_protein: int = 160
    target_form_carbs: int = 220
    target_form_fat: int = 65

    def set_active_tab(self, val: str):
        self.active_tab = val

    def set_chat_input(self, val: str):
        self.chat_input = val

    def set_show_meal_modal(self, val: bool):
        self.show_meal_modal = val

    def set_meal_form_name(self, val: str):
        self.meal_form_name = val

    def set_meal_form_category(self, val: str):
        self.meal_form_category = val

    def set_meal_form_calories(self, val: str):
        try:
            self.meal_form_calories = int(val)
        except ValueError:
            pass

    def set_meal_form_protein(self, val: str):
        try:
            self.meal_form_protein = int(val)
        except ValueError:
            pass

    def set_meal_form_carbs(self, val: str):
        try:
            self.meal_form_carbs = int(val)
        except ValueError:
            pass

    def set_meal_form_fat(self, val: str):
        try:
            self.meal_form_fat = int(val)
        except ValueError:
            pass

    def set_show_recipe_modal(self, val: bool):
        self.show_recipe_modal = val

    def set_recipe_form_name(self, val: str):
        self.recipe_form_name = val

    def set_recipe_form_ingredients(self, val: str):
        self.recipe_form_ingredients = val

    def set_recipe_form_servings(self, val: str):
        try:
            self.recipe_form_servings = int(val)
        except ValueError:
            pass

    def set_recipe_form_calories(self, val: str):
        try:
            self.recipe_form_calories = int(val)
        except ValueError:
            pass

    def set_recipe_form_protein(self, val: str):
        try:
            self.recipe_form_protein = int(val)
        except ValueError:
            pass

    def set_recipe_form_carbs(self, val: str):
        try:
            self.recipe_form_carbs = int(val)
        except ValueError:
            pass

    def set_recipe_form_fat(self, val: str):
        try:
            self.recipe_form_fat = int(val)
        except ValueError:
            pass

    def set_show_target_modal(self, val: bool):
        self.show_target_modal = val

    def set_target_form_calories(self, val: str):
        try:
            self.target_form_calories = int(val)
        except ValueError:
            pass

    def set_target_form_protein(self, val: str):
        try:
            self.target_form_protein = int(val)
        except ValueError:
            pass

    def set_target_form_carbs(self, val: str):
        try:
            self.target_form_carbs = int(val)
        except ValueError:
            pass

    def set_target_form_fat(self, val: str):
        try:
            self.target_form_fat = int(val)
        except ValueError:
            pass


    # -----------------------------
    # COMPUTED VARS
    # -----------------------------
    @rx.var
    def total_calories(self) -> int:
        return sum(int(m.get("calories", 0)) for m in self.logged_meals)

    @rx.var
    def total_protein(self) -> int:
        return sum(int(m.get("protein", 0)) for m in self.logged_meals)

    @rx.var
    def total_carbs(self) -> int:
        return sum(int(m.get("carbs", 0)) for m in self.logged_meals)

    @rx.var
    def total_fat(self) -> int:
        return sum(int(m.get("fat", 0)) for m in self.logged_meals)

    @rx.var
    def remaining_calories(self) -> int:
        rem = self.target_calories - self.total_calories
        return max(0, rem)

    @rx.var
    def remaining_protein(self) -> int:
        rem = self.target_protein - self.total_protein
        return max(0, rem)

    @rx.var
    def calorie_percentage(self) -> int:
        if self.target_calories <= 0:
            return 0
        pct = int((self.total_calories / self.target_calories) * 100)
        return min(100, max(0, pct))

    @rx.var
    def protein_percentage(self) -> int:
        if self.target_protein <= 0:
            return 0
        pct = int((self.total_protein / self.target_protein) * 100)
        return min(100, max(0, pct))

    @rx.var
    def carbs_percentage(self) -> int:
        if self.target_carbs <= 0:
            return 0
        pct = int((self.total_carbs / self.target_carbs) * 100)
        return min(100, max(0, pct))

    @rx.var
    def fat_percentage(self) -> int:
        if self.target_fat <= 0:
            return 0
        pct = int((self.total_fat / self.target_fat) * 100)
        return min(100, max(0, pct))

    @rx.var
    def is_calorie_over(self) -> bool:
        return self.total_calories > self.target_calories

    @rx.var
    def meal_count(self) -> int:
        return len(self.logged_meals)

    @rx.var
    def recipe_count(self) -> int:
        return len(self.recipes)

    # -----------------------------
    # EVENT HANDLERS - MEALS
    # -----------------------------
    def open_add_meal(self):
        self.is_editing_meal = False
        self.meal_form_id = f"m_{int(datetime.datetime.now().timestamp())}"
        self.meal_form_name = ""
        self.meal_form_category = "Snack"
        self.meal_form_calories = 300
        self.meal_form_protein = 25
        self.meal_form_carbs = 30
        self.meal_form_fat = 10
        self.show_meal_modal = True

    def open_edit_meal(self, meal: dict):
        self.is_editing_meal = True
        self.meal_form_id = meal.get("id", "")
        self.meal_form_name = meal.get("name", "")
        self.meal_form_category = meal.get("category", "Lunch")
        self.meal_form_calories = int(meal.get("calories", 0))
        self.meal_form_protein = int(meal.get("protein", 0))
        self.meal_form_carbs = int(meal.get("carbs", 0))
        self.meal_form_fat = int(meal.get("fat", 0))
        self.show_meal_modal = True

    def close_meal_modal(self):
        self.show_meal_modal = False

    def save_meal(self):
        if not self.meal_form_name.strip():
            return
        
        now_str = datetime.datetime.now().strftime("%I:%M %p")
        meal_data = {
            "id": self.meal_form_id or f"m_{int(datetime.datetime.now().timestamp())}",
            "name": self.meal_form_name.strip(),
            "category": self.meal_form_category,
            "calories": self.meal_form_calories,
            "protein": self.meal_form_protein,
            "carbs": self.meal_form_carbs,
            "fat": self.meal_form_fat,
            "time": now_str,
        }

        if self.is_editing_meal:
            updated = []
            for m in self.logged_meals:
                if m.get("id") == self.meal_form_id:
                    updated.append(meal_data)
                else:
                    updated.append(m)
            self.logged_meals = updated
        else:
            self.logged_meals.append(meal_data)

        self.show_meal_modal = False

    def delete_meal(self, meal_id: str):
        self.logged_meals = [m for m in self.logged_meals if m.get("id") != meal_id]

    def clear_all_meals(self):
        self.logged_meals = []

    # -----------------------------
    # EVENT HANDLERS - RECIPES
    # -----------------------------
    def open_add_recipe(self):
        self.is_editing_recipe = False
        self.recipe_form_id = f"r_{int(datetime.datetime.now().timestamp())}"
        self.recipe_form_name = ""
        self.recipe_form_ingredients = ""
        self.recipe_form_servings = 1
        self.recipe_form_calories = 450
        self.recipe_form_protein = 35
        self.recipe_form_carbs = 40
        self.recipe_form_fat = 12
        self.show_recipe_modal = True

    def open_edit_recipe(self, recipe: dict):
        self.is_editing_recipe = True
        self.recipe_form_id = recipe.get("id", "")
        self.recipe_form_name = recipe.get("name", "")
        self.recipe_form_ingredients = recipe.get("ingredients", "")
        self.recipe_form_servings = int(recipe.get("servings", 1))
        self.recipe_form_calories = int(recipe.get("calories", 0))
        self.recipe_form_protein = int(recipe.get("protein", 0))
        self.recipe_form_carbs = int(recipe.get("carbs", 0))
        self.recipe_form_fat = int(recipe.get("fat", 0))
        self.show_recipe_modal = True

    def close_recipe_modal(self):
        self.show_recipe_modal = False

    def save_recipe(self):
        if not self.recipe_form_name.strip():
            return

        recipe_data = {
            "id": self.recipe_form_id or f"r_{int(datetime.datetime.now().timestamp())}",
            "name": self.recipe_form_name.strip(),
            "ingredients": self.recipe_form_ingredients.strip() or "Standard ingredients",
            "servings": self.recipe_form_servings,
            "calories": self.recipe_form_calories,
            "protein": self.recipe_form_protein,
            "carbs": self.recipe_form_carbs,
            "fat": self.recipe_form_fat,
        }

        if self.is_editing_recipe:
            updated = []
            for r in self.recipes:
                if r.get("id") == self.recipe_form_id:
                    updated.append(recipe_data)
                else:
                    updated.append(r)
            self.recipes = updated
        else:
            self.recipes.append(recipe_data)

        self.show_recipe_modal = False

    def delete_recipe(self, recipe_id: str):
        self.recipes = [r for r in self.recipes if r.get("id") != recipe_id]

    def log_recipe_as_meal(self, recipe: dict):
        now_str = datetime.datetime.now().strftime("%I:%M %p")
        meal_data = {
            "id": f"m_{int(datetime.datetime.now().timestamp())}",
            "name": recipe.get("name", "Recipe Meal"),
            "category": "Dinner",
            "calories": int(recipe.get("calories", 0)),
            "protein": int(recipe.get("protein", 0)),
            "carbs": int(recipe.get("carbs", 0)),
            "fat": int(recipe.get("fat", 0)),
            "time": now_str,
        }
        self.logged_meals.append(meal_data)

    # -----------------------------
    # EVENT HANDLERS - TARGETS
    # -----------------------------
    def open_target_modal(self):
        self.target_form_calories = self.target_calories
        self.target_form_protein = self.target_protein
        self.target_form_carbs = self.target_carbs
        self.target_form_fat = self.target_fat
        self.show_target_modal = True

    def close_target_modal(self):
        self.show_target_modal = False

    def save_targets(self):
        self.target_calories = max(500, self.target_form_calories)
        self.target_protein = max(10, self.target_form_protein)
        self.target_carbs = max(10, self.target_form_carbs)
        self.target_fat = max(5, self.target_form_fat)
        self.show_target_modal = False

    # -----------------------------
    # CHATBOT AI ASSISTANT LOGIC
    # -----------------------------
    def send_chat_prompt(self, prompt_text: str):
        self.chat_input = prompt_text
        self.handle_chat_submit()

    def handle_chat_submit(self):
        text = self.chat_input.strip()
        if not text:
            return

        now_str = datetime.datetime.now().strftime("%I:%M %p")
        msg_id = f"c_{int(datetime.datetime.now().timestamp())}"
        
        user_msg = {
            "id": msg_id,
            "sender": "user",
            "text": text,
            "timestamp": now_str,
            "action": "",
        }
        self.chat_history.append(user_msg)
        self.chat_input = ""

        # Process user intent & construct AI response
        ai_reply, action_badge = self._process_ai_nlp(text)
        
        ai_msg = {
            "id": f"c_ai_{int(datetime.datetime.now().timestamp())}",
            "sender": "ai",
            "text": ai_reply,
            "timestamp": now_str,
            "action": action_badge,
        }
        self.chat_history.append(ai_msg)

    def _process_ai_nlp(self, text: str) -> tuple[str, str]:
        text_lower = text.lower()
        
        # 1. Action: CREATE / ADD RECIPE
        if "recipe" in text_lower or "create recipe" in text_lower or "save recipe" in text_lower:
            recipe_name = "Custom AI Recipe"
            # Extract title after 'recipe for' or 'recipe'
            match = re.search(r"recipe\s+(?:for\s+)?(['\"]?[\w\s\-]+['\"]?)", text, re.IGNORECASE)
            if match:
                recipe_name = match.group(1).strip("'\"").title()
            
            # Extract kcal and macros if present, else estimate
            kcal = self._extract_number(text, r"(\d+)\s*(?:kcal|calories)") or 450
            protein = self._extract_number(text, r"(\d+)\s*g?\s*protein") or 35
            carbs = self._extract_number(text, r"(\d+)\s*g?\s*(?:carbs|carb)") or 40
            fat = self._extract_number(text, r"(\d+)\s*g?\s*fat") or 12

            ingredients = text
            if ":" in text:
                ingredients = text.split(":", 1)[1].strip()

            new_recipe = {
                "id": f"r_{int(datetime.datetime.now().timestamp())}",
                "name": recipe_name,
                "ingredients": ingredients if len(ingredients) > 5 else "AI generated balanced ingredients",
                "servings": 1,
                "calories": kcal,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
            }
            self.recipes.append(new_recipe)
            return (
                f"✨ **Recipe Saved!**\n\nI've created and saved **{recipe_name}** to your recipes list:\n"
                f"- 🔥 **Calories:** {kcal} kcal\n"
                f"- 💪 **Protein:** {protein}g\n"
                f"- 🍞 **Carbs:** {carbs}g | 🥑 **Fat:** {fat}g\n\n"
                f"You can now log this recipe directly from your Recipes tab with one click!",
                "Recipe Created"
            )

        # 2. Action: LOG MEAL
        if any(k in text_lower for k in ["log", "ate", "had", "eat", "breakfast", "lunch", "dinner", "snack"]):
            category = "Snack"
            if "breakfast" in text_lower:
                category = "Breakfast"
            elif "lunch" in text_lower:
                category = "Lunch"
            elif "dinner" in text_lower:
                category = "Dinner"

            # Parse meal name
            meal_name = "Logged Meal"
            clean_text = re.sub(r"(?:log|ate|had|for breakfast|for lunch|for dinner|for snack|\d+\s*kcal|\d+\s*g\s*protein|\d+\s*g)", "", text, flags=re.IGNORECASE).strip(" :,.")
            if clean_text:
                meal_name = clean_text.title()
                if len(meal_name) > 40:
                    meal_name = meal_name[:37] + "..."
            else:
                meal_name = f"{category} Entry"

            # Parse or estimate macros
            kcal = self._extract_number(text, r"(\d+)\s*(?:kcal|calories)")
            protein = self._extract_number(text, r"(\d+)\s*g?\s*protein")
            carbs = self._extract_number(text, r"(\d+)\s*g?\s*(?:carbs|carb)")
            fat = self._extract_number(text, r"(\d+)\s*g?\s*fat")

            # Smart nutritional estimation fallback if numbers weren't explicitly provided
            if kcal is None:
                kcal, protein, carbs, fat = self._estimate_food_macros(text_lower)

            if protein is None:
                protein = max(5, int(kcal * 0.25 / 4))
            if carbs is None:
                carbs = max(5, int(kcal * 0.45 / 4))
            if fat is None:
                fat = max(2, int(kcal * 0.30 / 9))

            now_str = datetime.datetime.now().strftime("%I:%M %p")
            new_meal = {
                "id": f"m_{int(datetime.datetime.now().timestamp())}",
                "name": meal_name,
                "category": category,
                "calories": kcal,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
                "time": now_str,
            }
            self.logged_meals.append(new_meal)

            rem_k = self.target_calories - self.total_calories
            rem_p = self.target_protein - self.total_protein

            return (
                f"📝 **Meal Logged Successfully!**\n\n"
                f"Added **{meal_name}** ({category}):\n"
                f"- 🔥 **{kcal} kcal** | 💪 **{protein}g Protein** | 🍞 **{carbs}g Carbs** | 🥑 **{fat}g Fat**\n\n"
                f"📊 **Daily Status:** {self.total_calories}/{self.target_calories} kcal "
                f"({max(0, rem_k)} kcal remaining), {self.total_protein}/{self.target_protein}g Protein remaining.",
                "Meal Logged"
            )

        # 3. Action: DELETE MEAL / CLEAR
        if "delete" in text_lower or "remove" in text_lower or "clear" in text_lower:
            if "last" in text_lower and len(self.logged_meals) > 0:
                removed = self.logged_meals.pop()
                return (f"🗑️ Removed your last logged meal: **{removed.get('name')}**.", "Meal Deleted")
            elif "all" in text_lower:
                self.logged_meals = []
                return ("🗑️ Cleared all logged meals for today.", "Meals Cleared")

        # 4. Action: SET TARGET GOALS
        if "target" in text_lower or "goal" in text_lower or "set calories" in text_lower:
            new_c = self._extract_number(text, r"(\d+)\s*(?:kcal|calories)")
            new_p = self._extract_number(text, r"(\d+)\s*g?\s*protein")
            if new_c:
                self.target_calories = new_c
            if new_p:
                self.target_protein = new_p
            return (
                f"🎯 **Goal Updated!**\n\n"
                f"- New Calorie Target: **{self.target_calories} kcal**\n"
                f"- New Protein Target: **{self.target_protein}g**",
                "Goal Updated"
            )

        # 5. Query: REMAINING MACROS / STATUS
        if any(k in text_lower for k in ["left", "remaining", "status", "summary", "how much", "target"]):
            rem_k = self.target_calories - self.total_calories
            rem_p = self.target_protein - self.total_protein
            rem_c = self.target_carbs - self.total_carbs
            rem_f = self.target_fat - self.total_fat
            
            k_status = f"{rem_k} kcal left" if rem_k >= 0 else f"{-rem_k} kcal OVER limit!"
            p_status = f"{rem_p}g left" if rem_p >= 0 else f"Goal reached (+{-rem_p}g)!"

            return (
                f"📊 **Here is your current daily summary:**\n\n"
                f"- 🔥 **Calories:** {self.total_calories} / {self.target_calories} kcal ({k_status})\n"
                f"- 💪 **Protein:** {self.total_protein} / {self.target_protein}g ({p_status})\n"
                f"- 🍞 **Carbs:** {self.total_carbs} / {self.target_carbs}g ({rem_c}g left)\n"
                f"- 🥑 **Fat:** {self.total_fat} / {self.target_fat}g ({rem_f}g left)\n\n"
                f"Log another meal or ask for recipe recommendations whenever you're ready!",
                "Status Check"
            )

        # 6. Default AI Assistant Nutrition Advice / Meal Suggestion
        rem_p = max(0, self.target_protein - self.total_protein)
        rem_k = max(0, self.target_calories - self.total_calories)
        return (
            f"💡 **AI Nutrition Recommendation:**\n\n"
            f"Based on your query and current macros ({rem_p}g protein remaining, {rem_k} kcal remaining):\n\n"
            f"• **High-Protein Suggestion:** Grilled chicken breast (200g) with steamed broccoli & brown rice (~420 kcal, 46g P).\n"
            f"• **Quick Snack Option:** 200g Greek Yogurt with 30g almonds (~250 kcal, 22g P).\n\n"
            f"Tell me what you decide to eat and I'll log it for you!",
            "AI Recommendation"
        )

    def _extract_number(self, text: str, pattern: str) -> int | None:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None

    def _estimate_food_macros(self, text: str) -> tuple[int, int, int, int]:
        """Estimate calories, protein, carbs, fat based on keywords."""
        if "egg" in text:
            return (210, 18, 2, 14)
        if "chicken" in text or "turkey" in text:
            return (350, 48, 10, 8)
        if "steak" in text or "beef" in text:
            return (480, 52, 0, 26)
        if "salmon" in text or "fish" in text:
            return (400, 36, 0, 22)
        if "shake" in text or "whey" in text or "protein powder" in text:
            return (220, 30, 12, 3)
        if "yogurt" in text or "curd" in text:
            return (180, 20, 12, 4)
        if "pizza" in text or "burger" in text:
            return (680, 28, 70, 32)
        if "salad" in text:
            return (280, 18, 20, 12)
        # default fallback
        return (350, 25, 35, 10)


