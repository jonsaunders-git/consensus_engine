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

    @classmethod
    def all_states(cls):
        return [key.value for key in cls]

    @classmethod
    def reporting_as_state(cls, state):
        # on-hold and archived proposals always report results from published state
        if state in {ProposalState.ON_HOLD, ProposalState.ARCHIVED}:
            return ProposalState.PUBLISHED
        else:
            return state

    def get_next_states(self):
        """ Returns a list of all the possible next states given a current state """
        # implemented this as a definition rather than something more optimised for readability
        if self.value == ProposalState.DRAFT:
            next_states = [ProposalState.TRIAL,
                           ProposalState.PUBLISHED,
                           ProposalState.ON_HOLD,
                           ProposalState.ARCHIVED]
        elif self.value == ProposalState.TRIAL:
            next_states = [ProposalState.PUBLISHED,
                           ProposalState.ON_HOLD,
                           ProposalState.ARCHIVED]
        elif self.value == ProposalState.PUBLISHED:
            next_states = [ProposalState.ON_HOLD,
                           ProposalState.ARCHIVED]
        elif self.value == ProposalState.ON_HOLD:
            next_states = [ProposalState.PUBLISHED,
                           ProposalState.ARCHIVED]
        elif self.value == ProposalState.ARCHIVED:
            next_states = []
        return next_states
