class ExplainabilityTreeGenerator:
    """
    Constructs a tree-structured explanation of the decision process.
    """

    @classmethod
    def generate_tree(cls, strategy_id: str, strategy_details: dict,
                      dimension_scores: dict, individual_scores: dict,
                      strategy_weights: dict, feature_weights: dict) -> dict:
        """
        Builds a hierarchical decision tree.
        """
        strat_weight_config = strategy_weights.get(strategy_id, {})
        
        # Level 1: Final Decision Node
        tree = {
            "name": f"決策模型: {strategy_details['name']}",
            "value": f"{strategy_details['score']:.1f} 分 ({strategy_details['rating']})",
            "type": "root",
            "description": strategy_details["philosophy"],
            "summary": strategy_details["summary"],
            "children": []
        }
        
        # Level 2: Fused Dimensions
        # Dimensions sorted by weight descending in the strategy
        dim_weights = [(dim, w) for dim, w in strat_weight_config.items() if dim not in ["name", "philosophy"]]
        dim_weights.sort(key=lambda x: x[1], reverse=True)
        
        # Translate dimension names
        dim_names = {
            "growth": "成長能力",
            "quality": "企業品質",
            "safety": "財務安全",
            "valuation": "估值合理性",
            "momentum": "市場動能"
        }
        
        dim_icons = {
            "growth": "📈",
            "quality": "💎",
            "safety": "🛡️",
            "valuation": "🏷️",
            "momentum": "⚡"
        }
        
        for dim, w in dim_weights:
            dim_score = dimension_scores.get(dim, 50.0)
            dim_node = {
                "name": f"{dim_icons.get(dim, '')} {dim_names.get(dim, dim)}",
                "value": f"{dim_score:.1f} 分 (權重: {w*100:.0f}%)",
                "type": "dimension",
                "description": f"此面向對最終得分貢獻了 {dim_score * w:.1f} 分。",
                "children": []
            }
            
            # Level 3: Individual Features
            # Features sorted by weight descending
            f_weights = [(feat, fw) for feat, fw in feature_weights.get(dim, {}).items()]
            f_weights.sort(key=lambda x: x[1], reverse=True)
            
            for feat, fw in f_weights:
                if feat in individual_scores:
                    f_detail = individual_scores[feat]
                    feat_node = {
                        "name": f_detail["reason"].split("為")[0].strip(), # Get name
                        "value": f"{f_detail['score']:.1f} 分 (權重: {fw*100:.0f}%)",
                        "type": "feature",
                        "description": f_detail["reason"]
                    }
                    dim_node["children"].append(feat_node)
                    
            tree["children"].append(dim_node)
            
        return tree
