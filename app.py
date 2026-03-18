from flask import Flask, render_template, request
import random
import requests

app = Flask(__name__)

CITY_COORDS = {
    "Seattle": {"latitude": 47.6062, "longitude": -122.3321},
    "Bangkok": {"latitude": 13.7563, "longitude": 100.5018},
    "Los Angeles": {"latitude": 34.0522, "longitude": -118.2437},
    "New York": {"latitude": 40.7128, "longitude": -74.0060},
}

DRILLS = [
    {
        "name": "Mini Tennis Warmup",
        "category": "warmup",
        "skill_levels": ["beginner", "intermediate", "advanced"],
        "focus": ["all"],
        "minutes": 10,
        "description": "Start close to the net and rally softly to build rhythm and control.",
        "equipment": "racket, tennis balls",
    },
    {
        "name": "Dynamic Movement Warmup",
        "category": "warmup",
        "skill_levels": ["beginner", "intermediate", "advanced"],
        "focus": ["all"],
        "minutes": 5,
        "description": "Do light jogging, side shuffles, lunges, and arm circles.",
        "equipment": "none",
    },
    {
        "name": "Crosscourt Forehand Rally",
        "category": "groundstrokes",
        "skill_levels": ["beginner", "intermediate", "advanced"],
        "focus": ["groundstrokes"],
        "minutes": 12,
        "description": "Rally crosscourt on the forehand side and focus on consistency and depth.",
        "equipment": "racket, tennis balls",
    },
    {
        "name": "Backhand Consistency Drill",
        "category": "groundstrokes",
        "skill_levels": ["beginner", "intermediate", "advanced"],
        "focus": ["groundstrokes"],
        "minutes": 12,
        "description": "Practice repeatable backhands with good net clearance and balance.",
        "equipment": "racket, tennis balls",
    },
    {
        "name": "Alternating Forehand and Backhand",
        "category": "groundstrokes",
        "skill_levels": ["intermediate", "advanced"],
        "focus": ["groundstrokes"],
        "minutes": 15,
        "description": "Alternate forehands and backhands to improve movement and recovery.",
        "equipment": "racket, tennis balls",
    },
    {
        "name": "Target Serving",
        "category": "serves",
        "skill_levels": ["beginner", "intermediate", "advanced"],
        "focus": ["serves"],
        "minutes": 12,
        "description": "Serve to targets in both service boxes and focus on placement.",
        "equipment": "racket, tennis balls, cones",
    },
    {
        "name": "Second Serve Repetition",
        "category": "serves",
        "skill_levels": ["intermediate", "advanced"],
        "focus": ["serves"],
        "minutes": 10,
        "description": "Hit second serves with extra spin and margin over the net.",
        "equipment": "racket, tennis balls",
    },
    {
        "name": "Serve Plus One",
        "category": "serves",
        "skill_levels": ["intermediate", "advanced"],
        "focus": ["serves", "matchplay"],
        "minutes": 15,
        "description": "Serve and attack the next ball to practice point starting patterns.",
        "equipment": "racket, tennis balls",
    },
    {
        "name": "Approach and Volley",
        "category": "netplay",
        "skill_levels": ["intermediate", "advanced"],
        "focus": ["netplay"],
        "minutes": 12,
        "description": "Hit an approach shot, move forward, and finish at the net.",
        "equipment": "racket, tennis balls",
    },
    {
        "name": "Reflex Volley Drill",
        "category": "netplay",
        "skill_levels": ["advanced"],
        "focus": ["netplay"],
        "minutes": 10,
        "description": "Practice quick reactions and compact volleys close to the net.",
        "equipment": "racket, tennis balls",
    },
    {
        "name": "Baseline Points",
        "category": "matchplay",
        "skill_levels": ["beginner", "intermediate", "advanced"],
        "focus": ["matchplay"],
        "minutes": 15,
        "description": "Play baseline points and focus on consistency and shot selection.",
        "equipment": "racket, tennis balls",
    },
    {
        "name": "Tie Break Practice",
        "category": "matchplay",
        "skill_levels": ["intermediate", "advanced"],
        "focus": ["matchplay"],
        "minutes": 15,
        "description": "Play practice tie breaks to simulate pressure situations.",
        "equipment": "racket, tennis balls",
    },
    {
        "name": "Cool Down Rally",
        "category": "cooldown",
        "skill_levels": ["beginner", "intermediate", "advanced"],
        "focus": ["all"],
        "minutes": 5,
        "description": "End with relaxed rallying at lower intensity.",
        "equipment": "racket, tennis balls",
    },
    {
        "name": "Stretch and Recovery",
        "category": "cooldown",
        "skill_levels": ["beginner", "intermediate", "advanced"],
        "focus": ["all"],
        "minutes": 5,
        "description": "Stretch calves, hamstrings, shoulders, and hips after practice.",
        "equipment": "water bottle, towel",
    },
]


def get_weather(city_name):
    coords = CITY_COORDS[city_name]
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "daily": "temperature_2m_max,precipitation_probability_max,wind_speed_10m_max",
        "timezone": "auto",
        "forecast_days": 1,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    daily = data["daily"]

    return {
        "temperature_max": daily["temperature_2m_max"][0],
        "precipitation_probability_max": daily["precipitation_probability_max"][0],
        "wind_speed_max": daily["wind_speed_10m_max"][0],
    }


def get_weather_recommendation(weather):
    rain = weather["precipitation_probability_max"]
    wind = weather["wind_speed_max"]
    temp = weather["temperature_max"]

    if rain >= 60:
        return "High chance of rain. Indoor court strongly recommended."
    if wind >= 25:
        return "Wind is strong. Outdoor practice may be difficult, especially for serving."
    if temp >= 32:
        return "It will be hot. Bring extra water and take more breaks."
    if temp <= 8:
        return "It will be cold. Warm up thoroughly before starting."
    return "Weather looks reasonable for outdoor practice."


def filter_main_drills(skill_level, focus_area):
    matching_drills = []

    for drill in DRILLS:
        if drill["category"] in ["warmup", "cooldown"]:
            continue

        correct_skill = skill_level in drill["skill_levels"]
        correct_focus = focus_area in drill["focus"]

        if correct_skill and correct_focus:
            matching_drills.append(drill)

    return matching_drills


def build_session(total_minutes, skill_level, focus_area):
    warmups = [drill for drill in DRILLS if drill["category"] == "warmup"]
    cooldowns = [drill for drill in DRILLS if drill["category"] == "cooldown"]
    main_drills = filter_main_drills(skill_level, focus_area)

    if not main_drills:
        return []

    random.shuffle(warmups)
    random.shuffle(cooldowns)
    random.shuffle(main_drills)

    session = []
    warmup = warmups[0]
    cooldown = cooldowns[0]

    session.append(warmup)

    remaining_minutes = total_minutes - warmup["minutes"] - cooldown["minutes"]

    if remaining_minutes < 10:
        return []

    drill_index = 0

    while remaining_minutes >= 10:
        possible_drills = []

        for drill in main_drills:
            if drill["minutes"] <= remaining_minutes:
                possible_drills.append(drill)

        if len(possible_drills) == 0:
            break

        chosen_drill = possible_drills[drill_index % len(possible_drills)]
        session.append(chosen_drill)
        remaining_minutes -= chosen_drill["minutes"]
        drill_index += 1

    session.append(cooldown)
    return session


def calculate_total_minutes(session):
    total = 0

    for drill in session:
        total += drill["minutes"]

    return total


def get_equipment_list(session):
    equipment_set = set()

    for drill in session:
        items = drill["equipment"].split(",")
        for item in items:
            cleaned_item = item.strip()
            if cleaned_item != "none":
                equipment_set.add(cleaned_item)

    return sorted(equipment_set)


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None

    if request.method == "POST":
        city = request.form.get("city")
        skill_level = request.form.get("skill_level")
        focus_area = request.form.get("focus_area")
        total_minutes = request.form.get("total_minutes")

        try:
            total_minutes = int(total_minutes)
        except ValueError:
            total_minutes = 0

        if total_minutes < 20:
            error = "Please enter at least 20 minutes."
        else:
            try:
                weather = get_weather(city)
                recommendation = get_weather_recommendation(weather)
                session = build_session(total_minutes, skill_level, focus_area)

                if len(session) == 0:
                    error = "Could not build a session with those settings. Try more time."
                else:
                    result = {
                        "city": city,
                        "skill_level": skill_level.title(),
                        "focus_area": focus_area.title(),
                        "requested_minutes": total_minutes,
                        "actual_minutes": calculate_total_minutes(session),
                        "weather": weather,
                        "recommendation": recommendation,
                        "session": session,
                        "equipment": get_equipment_list(session),
                    }
            except requests.RequestException:
                error = "Could not load weather data right now. Please try again."

    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True)