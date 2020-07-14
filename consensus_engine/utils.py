from enum import IntEnum


class ProposalState(IntEnum):
    DRAFT = 0
    TRIAL = 1
    PUBLISHED = 2
    ON_HOLD = 3
    ARCHIVED = 4

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
