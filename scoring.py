"""
Consistency Scoring Module

Compares text claims against video analysis results and calculates
a consistency score with detailed breakdown per claim type.
"""

from typing import Dict, Any, List


def score_consistency(
    claims: Dict[str, Any],
    video_stats: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compute a consistency score between text claims and video analysis.
    
    Args:
        claims: Dictionary with extracted claims from text
                (people, cars, weapon_present - each can be None)
        video_stats: Dictionary with video analysis results
                     (people, cars, weapon_present, frames)
    
    Returns:
        Dictionary containing:
        - score: Integer from 0-100 representing consistency score
        - details: List of dictionaries with per-claim breakdown:
            - claim_type: "people" | "cars" | "weapon"
            - claim_value: The value from the text claim
            - video_value: The value detected in the video
            - result: "supported" | "partial" | "unsupported"
            - note: String explanation of the result
    """
    score = 100
    details = []
    
    # Score people claim
    if claims.get("people") is not None:
        claim_people = claims["people"]
        video_people = video_stats.get("people", 0)
        
        diff = abs(claim_people - video_people)
        
        if diff == 0:
            result = "supported"
            note = f"Exact match: {claim_people} people detected"
        elif diff <= 1:
            result = "partial"
            note = f"Close match: claimed {claim_people}, detected {video_people} (difference: {diff})"
            score -= 10
        else:
            result = "unsupported"
            note = f"Mismatch: claimed {claim_people}, detected {video_people} (difference: {diff})"
            score -= 30
        
        details.append({
            "claim_type": "people",
            "claim_value": claim_people,
            "video_value": video_people,
            "result": result,
            "note": note
        })
    
    # Score cars claim
    if claims.get("cars") is not None:
        claim_cars = claims["cars"]
        video_cars = video_stats.get("cars", 0)
        
        diff = abs(claim_cars - video_cars)
        
        if diff == 0:
            result = "supported"
            note = f"Exact match: {claim_cars} cars detected"
        elif diff <= 1:
            result = "partial"
            note = f"Close match: claimed {claim_cars}, detected {video_cars} (difference: {diff})"
            score -= 10
        else:
            result = "unsupported"
            note = f"Mismatch: claimed {claim_cars}, detected {video_cars} (difference: {diff})"
            score -= 30
        
        details.append({
            "claim_type": "cars",
            "claim_value": claim_cars,
            "video_value": video_cars,
            "result": result,
            "note": note
        })
    
    # Score weapon claim
    if claims.get("weapon_present") is not None:
        claim_weapon = claims["weapon_present"]
        video_weapon = video_stats.get("weapon_present", False)
        
        if claim_weapon == video_weapon:
            result = "supported"
            if claim_weapon:
                note = "Weapon presence matches: both indicate weapon present"
            else:
                note = "Weapon absence matches: both indicate no weapon"
        else:
            result = "unsupported"
            if claim_weapon and not video_weapon:
                note = "Mismatch: text claims weapon present, but no weapon detected in video"
            else:
                note = "Mismatch: text claims no weapon, but weapon detected in video"
            score -= 40
        
        details.append({
            "claim_type": "weapon",
            "claim_value": claim_weapon,
            "video_value": video_weapon,
            "result": result,
            "note": note
        })
    
    # Clamp score between 0 and 100
    score = max(0, min(100, score))
    
    return {
        "score": int(score),
        "details": details
    }

