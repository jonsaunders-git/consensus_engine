select text, count(ct.id)
from consensus_engine_proposalchoice pc
join consensus_engine_proposal p on p.id = pc.proposal_id
left outer join consensus_engine_choiceticket ct on ct.proposal_choice_id = pc.id
where proposal_group_id=32 
group by text;
