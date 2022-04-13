SELECT "consensus_engine_proposalchoice"."text",
SUM(CASE WHEN "consensus_engine_proposalchoice"."current_consensus" IS NULL THEN 0 ELSE "consensus_engine_proposalchoice"."current_consensus" END) AS "choice_votes"
FROM "consensus_engine_proposalchoice"
INNER JOIN "consensus_engine_proposal" ON ("consensus_engine_proposalchoice"."proposal_id" = "consensus_engine_proposal"."id")
WHERE ("consensus_engine_proposalchoice"."deactivated_date" IS NULL AND "consensus_engine_proposal"."proposal_group_id" = 32) 
GROUP BY "consensus_engine_proposalchoice"."text";
