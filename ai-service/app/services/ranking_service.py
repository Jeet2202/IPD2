from typing import List, Dict, Any

class RankingService:
    @staticmethod
    def rank_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sorts candidates by score in descending order and assigns a ranking.
        Input is a list of dicts containing worker info, score, confidence, reasons, etc.
        """
        # Sort by score descending
        ranked = sorted(candidates, key=lambda x: x['score'], reverse=True)
        
        # Assign ranking and confidence
        for index, candidate in enumerate(ranked):
            candidate['ranking'] = index + 1
            # Simple confidence calculation based on score proximity to 100
            confidence_val = min(100.0, candidate['score'] + 2.0) # slightly boost confidence
            candidate['confidence'] = f"{int(confidence_val)}%"
            
        return ranked
