"""
Text Parser Module

Extracts claims from text descriptions using regex patterns.
Supports extracting counts of people, cars, and weapon presence.
"""

from typing import Dict, Optional
import re


def word_to_number(word: str) -> Optional[int]:
    """
    Convert word numbers to integers.
    
    Args:
        word: Word representation of a number
    
    Returns:
        Integer value or None if not recognized
    """
    word_numbers = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
        'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
        'eighteen': 18, 'nineteen': 19, 'twenty': 20
    }
    return word_numbers.get(word.lower())


def extract_claims(text: str) -> Dict[str, Optional[object]]:
    """
    Parse text description to extract claims about people, cars, and weapons.
    
    Args:
        text: Raw text description of an incident
    
    Returns:
        Dictionary with extracted claims:
        - people: Optional[int] - number of people mentioned
        - cars: Optional[int] - number of cars/vehicles mentioned
        - weapon_present: Optional[bool] - whether weapon is mentioned (True/False/None)
    """
    if not text or not text.strip():
        return {
            "people": None,
            "cars": None,
            "weapon_present": None
        }
    
    text_lower = text.lower()
    claims = {
        "people": None,
        "cars": None,
        "weapon_present": None
    }
    
    # Pattern for extracting number of people
    # Matches: "one person", "two people", "3 men", "five persons", etc.
    people_patterns = [
        r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|\d+)\s+(people|persons|person|men|women|men|individuals)\b',
        r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|\d+)\s+person\b',
        r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|\d+)\s+people\b'
    ]
    
    for pattern in people_patterns:
        match = re.search(pattern, text_lower)
        if match:
            number_str = match.group(1)
            # Try to convert word to number
            num = word_to_number(number_str)
            if num is None:
                # Try parsing as integer
                try:
                    num = int(number_str)
                except ValueError:
                    continue
            if num is not None:
                claims["people"] = num
                break
    
    # Pattern for extracting number of cars/vehicles
    # Matches: "one car", "two vehicles", "3 cars", etc.
    car_patterns = [
        r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|\d+)\s+(cars|car|vehicles|vehicle|trucks|truck|automobiles|automobile)\b',
        r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|\d+)\s+car\b',
        r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|\d+)\s+cars\b'
    ]
    
    for pattern in car_patterns:
        match = re.search(pattern, text_lower)
        if match:
            number_str = match.group(1)
            num = word_to_number(number_str)
            if num is None:
                try:
                    num = int(number_str)
                except ValueError:
                    continue
            if num is not None:
                claims["cars"] = num
                break
    
    # Pattern for weapon presence/absence
    # Check for positive mentions (gun, weapon, firearm, knife)
    weapon_positive_patterns = [
        r'\b(gun|guns|weapon|weapons|firearm|firearms|knife|knives|pistol|pistols|rifle|rifles|handgun|handguns)\b'
    ]
    
    # Check for negative mentions (no gun, without weapon, etc.)
    weapon_negative_patterns = [
        r'\b(no|without|not|none)\s+(gun|guns|weapon|weapons|firearm|firearms|knife|knives)',
        r'\b(gun|guns|weapon|weapons|firearm|firearms|knife|knives)\s+(not|absent|missing)'
    ]
    
    has_positive = any(re.search(pattern, text_lower) for pattern in weapon_positive_patterns)
    has_negative = any(re.search(pattern, text_lower) for pattern in weapon_negative_patterns)
    
    if has_positive and not has_negative:
        claims["weapon_present"] = True
    elif has_negative:
        claims["weapon_present"] = False
    # If neither, leave as None (not mentioned)
    
    return claims

