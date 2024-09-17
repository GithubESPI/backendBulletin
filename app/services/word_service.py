import logging
import json
from datetime import datetime
from fastapi import HTTPException
import pandas as pd
from docxtpl import DocxTemplate
from app.core.config import settings
import os
import unicodedata
import math
import docx

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fonction pour lire la configuration des ECTS depuis un fichier JSON
def read_ects_config():
    with open(settings.ECTS_JSON_PATH, 'r') as file:
        data = json.load(file)
    return data

# Fonction pour normaliser une chaîne de caractères
def normalize_string(s):
    if not isinstance(s, str):
        s = str(s)
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

# Fonction pour extraire les notes et les coefficients depuis une chaîne de caractères
def extract_grades_and_coefficients(grade_str):
    grades_coefficients = []
    if not grade_str.strip():
        return grades_coefficients  # Retourne une liste vide si la chaîne est vide
    parts = grade_str.split(" - ")
    for part in parts:
        if "Absent au devoir" in part:
            continue
        try:
            if "(" in part:
                grade_part, coefficient_part = part.rsplit("(", 1)
                coefficient_part = coefficient_part.rstrip(")")
            else:
                grade_part = part
                coefficient_part = "1.0"
            grade = grade_part.replace(",", ".").strip()
            coefficient = coefficient_part.replace(",", ".").strip()
            
            # Remplacer 'CCHM' par 1
            if grade == 'CCHM':
                grade = '1'
            grades_coefficients.append((float(grade), float(coefficient)))
        except ValueError:
            # Ignorer les valeurs qui ne peuvent pas être converties en float ou ne sont pas au format attendu
            continue
    return grades_coefficients

# Fonction pour calculer la moyenne pondérée des notes
def calculate_weighted_average(notes, ects):
    if not notes or not ects:
        return 0.0

    # Filtrer les notes et les ects où ects est zéro
    filtered_notes = [note for note, ect in zip(notes, ects) if ect != 0]
    filtered_ects = [ect for ect in ects if ect != 0]

    # Si aucune note valide ne reste après filtrage, retourner 0.0
    if not filtered_notes or not filtered_ects:
        return 0.0

    total_grade = sum(note * ect for note, ect in zip(filtered_notes, filtered_ects))
    total_ects = sum(filtered_ects)
    
    return total_grade / total_ects if total_ects != 0 else 0

# Fonction pour générer les placeholders pour le document Word
def generate_placeholders(titles_row, case_config, student_data, current_date, ects_data):
    logger.debug(f"Received ECTS data: {ects_data}")
    placeholders = {
        "nomApprenant": student_data["Nom"],
        "etendugroupe": student_data["Étendu Groupe"],
        "dateNaissance": student_data["Date de Naissance"],
        "groupe": student_data["Nom Groupe"],
        "campus": student_data["Nom Site"],
        "justifiee": student_data["ABS justifiées"],
        "injustifiee": student_data["ABS injustifiées"],
        "retard": student_data["Retards"],
        "datedujour": current_date,
        "appreciations": student_data["Appreciations"],
        "CodeApprenant": student_data["CodeApprenant"]
    }

    # Mise à jour des placeholders en fonction de la clé du cas
    if case_config["key"] == "M1_S1":
        placeholders.update({
            "UE1_Title": titles_row[0],
            "matiere1": titles_row[1],
            "matiere2": titles_row[2],
            "matiere3": titles_row[3],
            "UE2_Title": titles_row[4],
            "matiere4": titles_row[5],
            "UE3_Title": titles_row[6],
            "matiere5": titles_row[7],
            "matiere6": titles_row[8],
            "UE4_Title": titles_row[9],
            "matiere7": titles_row[10],
            "matiere8": titles_row[11],
            "matiere9": titles_row[12],
            "matiere10": titles_row[13],
            "matiere11": titles_row[14],
            "matiere12": titles_row[15],
            "UESPE_Title": titles_row[16],
            "matiere13": titles_row[17],
            "matiere14": titles_row[18],
            "matiere15": titles_row[19],
        })
    elif case_config["key"] == "M1_S2":
        placeholders.update({
            "UE1_Title": titles_row[0],
            "matiere1": titles_row[1],
            "matiere2": titles_row[2],
            "matiere3": titles_row[3],
            "UE2_Title": titles_row[4],
            "matiere4": titles_row[5],
            "matiere5": titles_row[6],
            "UE3_Title": titles_row[7],
            "matiere6": titles_row[8],
            "matiere7": titles_row[9],
            "matiere8": titles_row[10],
            "matiere9": titles_row[11],
            "matiere10": titles_row[12],
            "matiere11": titles_row[13],
            "matiere12": titles_row[14],
            "UESPE_Title": titles_row[15],
            "matiere13": titles_row[16],
            "matiere14": titles_row[17],
            "matiere15": titles_row[18],
            "matiere16": titles_row[19],
        })
    elif case_config["key"] == "M2_S3_MAGI":
        placeholders.update({
            "UE1_Title": titles_row[0],
            "matiere1": titles_row[1],
            "matiere2": titles_row[2],
            "UE2_Title": titles_row[3],
            "matiere3": titles_row[4],
            "UE3_Title": titles_row[5],
            "matiere4": titles_row[6],
            "matiere5": titles_row[7],
            "matiere6": titles_row[8],
            "matiere7": titles_row[9],
            "matiere8": titles_row[10],
            "matiere9": titles_row[11],
            "UESPE_Title": titles_row[12],
            "matiere10": titles_row[13],
            "matiere11": titles_row[14],
            "matiere12": titles_row[15],
            "matiere13": titles_row[16],
        })
    elif case_config["key"] == "M2_S3_MEFIM":
        placeholders.update({
            "UE1_Title": titles_row[0],
            "matiere1": titles_row[1],
            "matiere2": titles_row[2],
            "UE2_Title": titles_row[3],
            "matiere3": titles_row[4],
            "UE3_Title": titles_row[5],
            "matiere4": titles_row[6],
            "matiere5": titles_row[7],
            "matiere6": titles_row[8],
            "matiere7": titles_row[9],
            "matiere8": titles_row[10],
            "matiere9": titles_row[11],
            "UESPE_Title": titles_row[12],
            "matiere10": titles_row[13],
            "matiere11": titles_row[14],
            "matiere12": titles_row[15],
            "matiere13": titles_row[16],
        })
    elif case_config["key"] == "M2_S3_MAPI":
        placeholders.update({
            "UE1_Title": titles_row[0],
            "matiere1": titles_row[1],
            "matiere2": titles_row[2],
            "UE2_Title": titles_row[3],
            "matiere3": titles_row[4],
            "UE3_Title": titles_row[5],
            "matiere4": titles_row[6],
            "matiere5": titles_row[7],
            "matiere6": titles_row[8],
            "matiere7": titles_row[9],
            "matiere8": titles_row[10],
            "matiere9": titles_row[11],
            "UESPE_Title": titles_row[12],
            "matiere10": titles_row[13],
            "matiere11": titles_row[14],
            "matiere12": titles_row[15],
            "matiere13": titles_row[16],
            "matiere14": titles_row[17],
        })
    elif case_config["key"] == "M2_S4":
        placeholders.update({
            "UE1_Title": titles_row[0],
            "matiere1": titles_row[1],
            "UE2_Title": titles_row[2],
            "matiere2": titles_row[3],
            "matiere3": titles_row[4],
            "UE3_Title": titles_row[5],
            "matiere4": titles_row[6],
            "matiere5": titles_row[7],
            "matiere6": titles_row[8],
            "matiere7": titles_row[9],
            "matiere8": titles_row[10],
            "UESPE_Title": titles_row[11],
            "matiere9": titles_row[12],
            "matiere10": titles_row[13],
            "matiere11": titles_row[14],
        })

    # Ajouter les valeurs ECTS aux placeholders, en masquant celles spécifiées
    for i in range(1, 17):
        if i not in case_config["hidden_ects"]:
            placeholders[f"ECTS{i}"] = ects_data.get(f"ECTS{i}", 0)

    return placeholders


def calculate_ue_state(notes):
    notes_between_8_and_10 = sum(8 <= note < 10 for note in notes)
    notes_below_8 = sum(note < 8 for note in notes)

    if all(note >= 10 for note in notes):
        return "VA", ["" for _ in notes]
    elif notes_between_8_and_10 == 1 and notes_below_8 == 0:
        return "VA", ["C" if 8 <= note < 10 else "" for note in notes]
    else:
        states = []
        for note in notes:
            if note < 8:
                states.append("R")
            elif 8 <= note < 10:
                states.append("R" if notes_below_8 > 0 or notes_between_8_and_10 > 1 else "C")
            else:
                states.append("")
        return "NV", states

# Modify the logic where "R" is assigned
def process_ue_notes(placeholders, ue_name, note_indices, grade_column_indices, student_data, case_config):
    ue_notes = []
    
    for i in note_indices:
        grade_str = str(student_data.iloc[grade_column_indices[i-1]]).strip() if pd.notna(student_data.iloc[grade_column_indices[i-1]]) else ""
        ects_value = placeholders.get(f"ECTS{i}", "")

        # Check if note is empty and ECTS is either empty or hidden
        if grade_str == "" and (ects_value == "" or i in case_config["hidden_ects"]):
            placeholders[f"note{i}"] = ""
            placeholders[f"etat{i}"] = ""
            ue_notes.append(None)
            continue

        if grade_str and grade_str != 'Note':
            grades_coefficients = extract_grades_and_coefficients(grade_str)
            individual_average = calculate_weighted_average([g[0] for g in grades_coefficients], [g[1] for g in grades_coefficients])
            if individual_average is not None:
                ue_notes.append(individual_average)
                placeholders[f"note{i}"] = f"{individual_average:.2f}" if individual_average else ""
            else:
                placeholders[f"note{i}"] = ""
                ue_notes.append(None)
        else:
            placeholders[f"note{i}"] = ""
            ue_notes.append(None)

        # Initialize state to empty string
        placeholders[f"etat{i}"] = ""

    # Calculate UE state based on valid notes
    valid_ue_notes = [note for note in ue_notes if note is not None]
    
    if valid_ue_notes:
        notes_between_8_and_10 = sum(8 <= note < 10 for note in valid_ue_notes)
        notes_below_8 = sum(note < 8 for note in valid_ue_notes)

        if all(note >= 10 for note in valid_ue_notes):
            placeholders[f"etat{ue_name}"] = "VA"
        elif notes_between_8_and_10 == 1 and notes_below_8 == 0:
            placeholders[f"etat{ue_name}"] = "VA"
            for i, note in zip(note_indices, valid_ue_notes):
                if 8 <= note < 10 and placeholders[f"note{i}"] != "" and (placeholders.get(f"ECTS{i}", "") != "" and i not in case_config["hidden_ects"]):
                    placeholders[f"etat{i}"] = "C"
        else:
            placeholders[f"etat{ue_name}"] = "NV"
            for i, note in zip(note_indices, valid_ue_notes):
                if placeholders[f"note{i}"] != "" and (placeholders.get(f"ECTS{i}", "") != "" and i not in case_config["hidden_ects"]):
                    if note < 8 or (notes_between_8_and_10 > 1 and notes_below_8 > 0):
                        placeholders[f"etat{i}"] = "R"
                    elif 8 <= note < 10:
                        placeholders[f"etat{i}"] = "C"
    else:
        placeholders[f"etat{ue_name}"] = ""

        
# Fonction pour générer un document Word à partir des données de l'étudiant et du template
def generate_word_document(student_data, case_config, template_path, output_dir):
    ects_config = read_ects_config()
    current_date = datetime.now().strftime("%d/%m/%Y")
    group_name = student_data["Nom Groupe"]
    is_relevant_group = group_name in settings.RELEVANT_GROUPS
    logger.debug("Processing document for group: %s", group_name)

    # Corriger la clé du cas si nécessaire
    corrected_key = case_config["key"].replace("_", "-")

    ects_data_key = corrected_key
    if corrected_key == "M2_S3_MAGI_MEFIM":
        if "MAGI" in student_data["Nom Groupe"]:
            ects_data_key = "M2-S3-MAGI"
        elif "MEFIM" in student_data["Nom Groupe"]:
            ects_data_key = "M2-S3-MEFIM"

    ects_data = ects_config.get(ects_data_key, [{}])[0]
    logger.debug(f"ECTS data for {corrected_key}: {ects_data}")

    placeholders = generate_placeholders(case_config["titles_row"], case_config, student_data, current_date, ects_data)

    # New logic for M1-S1
    if case_config["key"] == "M1_S1":
        process_ue_notes(placeholders, "UE1", [1, 2, 3], case_config["grade_column_indices"], student_data, case_config)
        process_ue_notes(placeholders, "UE2", [4], case_config["grade_column_indices"], student_data, case_config)
        process_ue_notes(placeholders, "UE3", [5, 6], case_config["grade_column_indices"], student_data, case_config)
        process_ue_notes(placeholders, "UE4", [7, 8, 9, 10, 11, 12], case_config["grade_column_indices"], student_data, case_config)
        process_ue_notes(placeholders, "UESPE", [13, 14, 15], case_config["grade_column_indices"], student_data, case_config)

        # Get UE1 notes, treating empty strings as None
        ue1_notes = [float(placeholders[f"note{i}"]) if placeholders[f"note{i}"] and placeholders[f"note{i}"] != "" and i not in case_config["hidden_ects"] and placeholders.get(f"ECTS{i}", "") != "" else None for i in range(1, 4)]

        # Initialize all states to empty string
        placeholders["etatUE1"] = ""
        for i in range(1, 4):
            placeholders[f"etat{i}"] = ""

        # Only process if there are any non-None values
        if any(note is not None for note in ue1_notes):
            # Count notes in different ranges, ignoring None values
            notes_between_8_and_10 = sum(8 <= note < 10 for note in ue1_notes if note is not None)
            notes_below_8 = sum(note < 8 for note in ue1_notes if note is not None)

            # Determine UE1 state and individual states
            if all(note >= 10 for note in ue1_notes if note is not None):
                placeholders["etatUE1"] = "VA"
            elif notes_between_8_and_10 == 1 and notes_below_8 == 0:
                placeholders["etatUE1"] = "VA"
                for i, note in enumerate(ue1_notes, start=1):
                    if note is not None and 8 <= note < 10 and i not in case_config["hidden_ects"] and placeholders.get(f"ECTS{i}", "") != "":
                        placeholders[f"etat{i}"] = "C"
            else:
                placeholders["etatUE1"] = "NV"
                for i, note in enumerate(ue1_notes, start=1):
                    if note is not None and i not in case_config["hidden_ects"] and placeholders.get(f"ECTS{i}", "") != "":
                        if note < 8:
                            placeholders[f"etat{i}"] = "R"
                        elif 8 <= note < 10:
                            placeholders[f"etat{i}"] = "R" if notes_below_8 > 0 or notes_between_8_and_10 > 1 else "C"
                        else:
                            placeholders[f"etat{i}"] = ""
                    else:
                        placeholders[f"etat{i}"] = ""
        else:
            # If all notes are None or empty, set all states to empty string
            placeholders["etatUE1"] = ""
            for i in range(1, 4):
                placeholders[f"etat{i}"] = ""



    total_ects = 0  # Initialiser le total des ECTS

    for i, col_index in enumerate(case_config["grade_column_indices"], start=1):
        grade_str = str(student_data.iloc[col_index]).strip() if pd.notna(student_data.iloc[col_index]) else ""
        if grade_str and grade_str != 'Note':
            grades_coefficients = extract_grades_and_coefficients(grade_str)
            individual_average = calculate_weighted_average([g[0] for g in grades_coefficients], [g[1] for g in grades_coefficients])
            placeholders[f"note{i}"] = f"{individual_average:.2f}" if individual_average else ""
            if individual_average > 8 and i not in case_config["hidden_ects"]:
                ects_value = int(ects_data.get(f"ECTS{i}", 1))  # Utiliser le coefficient par défaut 1 pour les ECTS masqués et convertir en int
                placeholders[f"ECTS{i}"] = ects_value
            elif individual_average > 0:
                placeholders[f"ECTS{i}"] = 0
            else:
                placeholders[f"ECTS{i}"] = ""
        else:
            placeholders[f"note{i}"] = ""
            placeholders[f"ECTS{i}"] = ""

    for ue, indices in case_config["ects_sum_indices"].items():
        ue_sum = 0
        ue_ects = 0

        for index in indices:
            note = float(placeholders[f"note{index}"]) if placeholders[f"note{index}"] not in ["", None] else 0
            ects = int(placeholders[f"ECTS{index}"]) if placeholders[f"ECTS{index}"] not in ["", None] else 0

            if ects != 0:
                ue_sum += note * ects
                ue_ects += ects

        count_valid_notes = len([index for index in indices if placeholders[f"note{index}"] not in ["", None]])
        average_ue = math.ceil(ue_sum / ue_ects * 100) / 100 if ue_ects > 0 else 0
        placeholders[f"moy{ue}"] = f"{average_ue:.2f}" if average_ue else ""
        placeholders[f"ECTS{ue}"] = ue_ects if ue_ects else ""
        total_ects += ue_ects

    placeholders["moyenneECTS"] = total_ects

    # Calcul de la moyenne générale en fonction des moyennes des UE
    total_ue_notes = sum(
        float(placeholders[f"moy{ue}"]) * int(placeholders[f"ECTS{ue}"])
        for ue in case_config["ects_sum_indices"].keys()
        if placeholders[f"moy{ue}"] not in ["", None] and placeholders[f"ECTS{ue}"] not in ["", 0, None]
    )
    total_ue_ects = sum(
        int(placeholders[f"ECTS{ue}"])
        for ue in case_config["ects_sum_indices"].keys()
        if placeholders[f"ECTS{ue}"] not in ["", 0, None]
    )

    # Calcul de la moyenne générale arrondie au centième près
    placeholders["moyenne"] = f"{math.ceil(total_ue_notes / total_ue_ects * 100) / 100:.2f}" if total_ue_ects else 0

    # Supprimer les placeholders pour les ECTS masqués du document final
    for hidden_ects in case_config["hidden_ects"]:
        placeholders.pop(f"ECTS{hidden_ects}", None)

    logger.debug(f"Placeholders: {placeholders}")  # Log des placeholders pour vérifier leurs valeurs

    doc = DocxTemplate(template_path)
    doc.render(placeholders)
    output_filename = f"{normalize_string(student_data['Nom'])}_bulletin.docx"
    output_filepath = os.path.join(output_dir, output_filename)
    doc.save(output_filepath)
    return output_filepath

