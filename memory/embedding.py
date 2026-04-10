class EmbeddingModel:
    """嵌入模型基类（最小接口）"""

    def encode(self, texts: str | list[str]):
        raise NotImplementedError

    @property
    def dimension(self) -> int:
        raise NotImplementedError


class LocalTransformerEmbedding(EmbeddingModel):
    """本地Transformer嵌入"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._backend = None
        self._st_model = None
        self._hf_tokenizer = None
        self._dimension = None
        self._load_backend()

    def _load_backend(self):
        pass
