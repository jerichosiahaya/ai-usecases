from src.llm.llm_sk import LLMService
from loguru import logger

class CVScoring:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def _calculate_score_matrix(self, score_attributes: list):
        total_score = 0
        score_attribute_details = score_attributes.get('attributes', [])
        for item in score_attribute_details:
            if 'subAttributes' in item and len(item['subAttributes']) == 1:
                score_calc = (item['subAttributes'][0]['percentage'] / 100) * item['scoreDistribution']
                total_score += score_calc


        score_attributes['totalScoreResult'] = total_score
        return score_attributes

    async def assess(self, predefined_score: str, candidate_data: str):
        try:
            result = await self.llm_service.score_cv(predefined_score, candidate_data)

            if not result:
                raise ValueError("No result returned from LLM service")
            
            result_score_attributes = result.get('data', [])
            if not result_score_attributes:
                raise ValueError("No scoring data found in the response")

            predefined_score_attributes = predefined_score.get('attributes', [])
            for predefined_item in predefined_score_attributes:
                for result_item in result_score_attributes:
                    if predefined_item['attributeName'] == result_item['attribute_name']:
                        predefined_item['subAttributes'] = result_item['attribute_details']
            
            final_result = self._calculate_score_matrix(predefined_score)

            return final_result
        except Exception as e:
            raise RuntimeError(f"Error scoring CV: {str(e)}")