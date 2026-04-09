class CCAgentsException(Exception):
    pass


class LLMException(CCAgentsException):
    pass


class AgentException(CCAgentsException):
    pass


class ConfigException(CCAgentsException):
    pass


class ToolException(CCAgentsException):
    pass
