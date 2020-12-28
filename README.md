# consensus_engine
Repo for open source version of consensus engine

# Work in progress
First Python and Django project developed during coronavirus lockdown
Open sourced (MIT licence) due to employment
Please review this with the understanding that I used it to learn django and python, thus many concepts may be immature

Welcome to the Consensus Engine 0.8
-----------------------------------

This application is a "work in progress" to build an engine to collect
the consensus of decision across an enterprise. The key concepts are
below, and currently the application allows only the basic
functionality.

### Key Concepts for Consensus Engine

\
 **Proposals**

Proposals are the key part of the Consensus Engine. Users create
proposals and ask people to vote on them to get a consensus of opinion
to show support for the proposal. Each proposal can have a set of
choices that any user can pick, and this is set up at creation time.
Currently you can change the choices and the choices, but this may not
be available in the future. Only the user who created the Proposal can
edit it.

**Votes**

Votes are cast for a proposal choice, a user can change their vote as
many times as wanted, but each vote is captured with only the last one
counting toward the consensus. By saving all the votes cast we can
analyse the state of the consensus over time. All the votes that a user
has cast can be found in the My Votes function on the task bar.

**Consensus**

The consensus is currently calculated as the option with the highest
number of votes, but the creator will be allowed to pick a general
calculation - i.e. % of votes, % of members of group, etc (we need to
review statistical analysis).

**Proposal Groups**

Proposals can be grouped under a single category, currently I am working
on the approach that we will only have one level of hierarchy to keep it
simple. Users can view and vote on the proposals within the groups they
are members of. You can join a group by selecting the icon on the group
in the Proposal Group list. Only the user that created the Group can
edit it

**Invites**

You can now invite other users to a Proposal Group. Use the person icon
againt the proposal group and add another user, they will then get an
invite, which they can either accept or decline. Accepting adds the
person to the group.

### Future Enhancements

-   There shoud be multiple owners of a proposal than can contribute to
    the proposal before publishing
-   Improved analysis of voting across time needs to be implemented
-   Mulitple different consensus calculation types
-   Allow for Group defaults for choice - so that consensus can be
    aggregated at Group level
-   Improvements in User Experience
-   Menu implementation for iPhone/SmartPhone
-   Statistics of current vote
-   News feed of changes to Group and Proposals
-   API connectivity to vote and get votes
-   Anonymity of voters
-   Tagging and searching to create more complex relationships between
    proposals
-   Implementation of user management, registration and permissions

### Release Notes for version 0.8

-   The number of proposals the user needs to still vote on is show in
    the sidebar.
-   The choices for all the proposals in a group can now be mandated
    -   When proposal within a group is published and there is no other
        proposals in published state the user will be asked if they want
        to make all proposals within the the group have the same set of
        choices
    -   The affect of saying "Yes" to this will be:
        -   All new proposals will default to the choices within the
            default proposal
        -   DRAFT and TRIAL proposals will not change, and you can add
            and remove choices as before, but when they are published
            the user will be told that the choices will change to the
            default, on publishing the choices will meet the default
        -   ON HOLD proposals will be archived and cannot be
            re-published
-   For proposals in a group that have a mandated choices you can get
    group statistics

\

### Release Notes for version 0.7

-   A person can be added to a trial after they become a member of
    trialling team
-   Members of groups can be listed

\

### Release Notes for version 0.6

-   You can now set a person who is a member of a group so that they can
    participate in trials.
-   Trial proposals are handled differently, and the votes will be
    cleared once the trial is over

\

### Release Notes for version 0.5

-   Added functionality for proposal states, these states are described
    below

    -   **DRAFT** - when a user creates a proposal, the status is draft,
        the user can edit the proposal and change the options the user
        can select
    -   **TRIAL** - a proposal can be put into trial with a small group
        to see if the proposal works and has all the options needed. All
        votes are specific to the trial and are not part of a published
        consensus
    -   **PUBLISHED** - a proposal can be published for people to create
        a consensus on the proposal
    -   **ON HOLD** - a proposal can be be put on hold from any state,
        and no changes or votes can be changed
    -   **ARCHIVED** - a proposal can be archived, so that it can be
        viewed but not edited at a later date, once archived cannot be
        re-published

\

### Release Notes for version 0.4

-   Added ablity to view the votes at a certain date by extending the
    URL for View Proposal

\

### Release Notes for version 0.3

-   Added CSS Graphs to View Proposal so the vote spread can be seen
    visually

\

### Release Notes for version 0.2

This is the second development release of the Consensus Engine
application.

-   Added "Invites" logic to the Proposal Group, a user can invite
    another to the group and they can accept or decline

\

### Release Notes for version 0.1

This is the first development release of the Consensus Engine
application.

-   Added Key Concepts to index to show how the application is built
-   Added tooltips for icons and links

\

