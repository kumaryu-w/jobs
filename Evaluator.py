from sentence_transformers import CrossEncoder

class Evaluator:
    def __init__(self, model_names:list, model_texts:list):
        if len(model_names) != len(model_texts):
            print(len(model_names),'!=', len(model_texts), "model text Error")
            return
        self.model_names = model_names
        self.model_texts = model_texts
        # print(len(model_texts))

    def fit(self, evaluate_texts:list):
        max_points = []
        total_score = 0
        for model_text in self.model_names:
            inputs = [(model_text, text) for text in evaluate_texts]
            points = self.evaluate(inputs)
            # print(points)
            max_points.append(max(points))
            total_score += max_points[-1]
        return max_points, total_score
    
    def evaluate(self, inputs:list):
        model = CrossEncoder('cross-encoder/stsb-roberta-large')
        scores = model.predict(inputs)
        return list(map(float, scores))





        