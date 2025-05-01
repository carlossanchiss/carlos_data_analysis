import openai, os
openai.api_key=os.environ.get("OPENAI_API_KEY","")

def generate_workout_plan(goal_json, cp, w_prime):
    prompt = (
        f"Eres entrenador de ciclismo. Basándote en el objetivo {goal_json}, "
        f"CP={cp} W y W'={w_prime} kJ, "
        "propón 3 sesiones (nombre, duración, bloques, TSS objetivo) para la próxima semana."
    )
    res=openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{"role":"user","content":prompt}])
    return res.choices[0].message.content
