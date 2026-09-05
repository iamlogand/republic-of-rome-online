import { ContextField } from "@/classes/AvailableAction"
import Accordion from "@/components/Accordion"

const factionLeaderDescription = (
  <p>Your faction leader will be immune from persuasion attempts.</p>
)

interface ActionDescriptionProps {
  actionName: string
  context: ContextField
}

const ActionDescription = ({ actionName, context }: ActionDescriptionProps) => {
  if (actionName === "Appoint Dictator") {
    return (
      <p>
        When Rome faces a military crisis, consuls may appoint a dictator, who
        takes over as HRAO and presiding magistrate. The Dictator must appoint a
        Master of Horse, and together they may be deployed to a single war.
      </p>
    )
  }
  if (actionName === "Attract knight") {
    return (
      <p>
        A senator may attempt to attract a knight. Each knight a senator
        controls increases their personal revenue and votes by +1.
      </p>
    )
  }
  if (actionName === "Pressure knight") {
    return (
      <p>
        Instead of attempting to attract a knight, you may pressure your
        senators' knights. Each pressured knight adds talents to its controlling
        senator's personal treasury, then is removed and no longer provides
        personal revenue or votes.
      </p>
    )
  }
  if (actionName === "Contribute") {
    return (
      <>
        <p>
          Senators may contribute talents to the State treasury, which increases
          their influence.
        </p>
        <div className="text-sm">
          <p>10 talents = +1 influence</p>
          <p>25 talents = +3 influence</p>
          <p>50 talents = +7 influence</p>
        </div>
      </>
    )
  }
  if (actionName === "Change faction leader") {
    return factionLeaderDescription
  }
  if (actionName === "Nominate Censor") {
    return (
      <p>
        The Censor oversees prosecutions of corrupt senators. Candidates must be
        prior consuls. The current Censor is eligible for re-election.
      </p>
    )
  }
  if (actionName === "Nominate Consul for Life") {
    return (
      <p>
        Any aligned senator in Rome with at least 21 influence may be nominated
        Consul for Life, even one already holding an office. The nominee adds
        his influence to his own vote. This can be proposed only once per turn
        and cannot be vetoed. Once elected, he cannot be assassinated, and his
        faction wins the game if he is still alive at the end of a revolution
        phase.
      </p>
    )
  }
  if (actionName === "Nominate consuls") {
    return (
      <p>
        Nominate two consuls for election. If the proposal passes, one will
        serve as Rome Consul and the other Field Consul.
      </p>
    )
  }
  if (actionName === "Pay for initiative") {
    return <p>Select a senator to pay {context.talents}T for the initiative.</p>
  }
  if (actionName === "Place bid") {
    return (
      <p>
        If you win, one of your senators must pay the bid after the auction.
      </p>
    )
  }
  if (actionName === "Propose major prosecution") {
    return (
      <p>
        If convicted, the accused will be executed and the prosecutor will gain
        influence.
      </p>
    )
  }
  if (actionName === "Propose minor prosecution") {
    return (
      <p>
        If convicted, the accused will lose popularity, influence, concessions
        and prior consul status, and the prosecutor will gain influence.
      </p>
    )
  }
  if (actionName === "Propose passing land bill") {
    return (
      <>
        <p>
          Land bills reduce unrest and increase the popularity of the sponsor
          and co-sponsor, at a cost to the State treasury.
        </p>
        <Accordion
          items={[
            {
              label: (
                <div className="flex items-baseline gap-2">
                  <span className="font-semibold">Type I</span>
                  <span className="text-sm">(−1 unrest)</span>
                </div>
              ),
              content: (
                <ul className="ml-10 list-disc text-sm">
                  <li>Costs 20T once</li>
                  <li>Sponsor gains 2 popularity</li>
                  <li>Co-sponsor gains 1 popularity</li>
                  <li>Allowed up to 1 bill of this type</li>
                </ul>
              ),
            },
            {
              label: (
                <div className="flex items-baseline gap-2">
                  <span className="font-semibold">Type II</span>
                  <span className="text-sm">(−2 unrest)</span>
                </div>
              ),
              content: (
                <ul className="ml-10 list-disc text-sm">
                  <li>Costs 5T/turn</li>
                  <li>Sponsor gains 2 popularity</li>
                  <li>Co-sponsor gains 1 popularity</li>
                  <li>Allowed up to 2 bills of this type</li>
                </ul>
              ),
            },
            {
              label: (
                <div className="flex items-baseline gap-2">
                  <span className="font-semibold">Type III</span>
                  <span className="text-sm">(−3 unrest)</span>
                </div>
              ),
              content: (
                <ul className="ml-10 list-disc text-sm">
                  <li>Costs 10T/turn</li>
                  <li>Sponsor gains 4 popularity</li>
                  <li>Co-sponsor gains 2 popularity</li>
                  <li>Allowed up to 3 bills of this type</li>
                </ul>
              ),
            },
          ]}
        />
      </>
    )
  }
  if (actionName === "Propose repealing land bill") {
    return (
      <>
        <p>
          Repealing a land bill removes its treasury cost but raises unrest and
          reduces the popularity of the sponsor and senators who vote for it.
          Only one repeal may be attempted per turn.
        </p>
        <Accordion
          items={[
            {
              label: (
                <div className="flex items-baseline gap-2">
                  <span className="font-semibold">Type II repeal</span>
                  <span className="text-sm">(+2 unrest)</span>
                </div>
              ),
              content: (
                <ul className="ml-10 list-disc text-sm">
                  <li>Saves 5T/turn</li>
                  <li>Sponsor loses 2 popularity</li>
                  <li>Senators who vote yea lose 1 popularity</li>
                </ul>
              ),
            },
            {
              label: (
                <div className="flex items-baseline gap-2">
                  <span className="font-semibold">Type III repeal</span>
                  <span className="text-sm">(+3 unrest)</span>
                </div>
              ),
              content: (
                <ul className="ml-10 list-disc text-sm">
                  <li>Saves 10T/turn</li>
                  <li>Sponsor loses 4 popularity</li>
                  <li>Senators who vote yea lose 2 popularity</li>
                </ul>
              ),
            },
          ]}
        />
      </>
    )
  }
  if (actionName === "Propose raising forces") {
    return (
      <p>
        Raising a legion or fleet costs the State {context.cost_per_unit}T
        {context.manpower_shortage === "True"
          ? ", increased from 10T due to a manpower shortage"
          : ""}
        , with a maintenance cost of 2T per turn.
      </p>
    )
  }
  if (actionName === "Propose disbanding forces") {
    return (
      <p>
        Disbanding a legion or fleet saves the State 2T per turn in maintenance. 
        You may only disband reserve forces, and cannot disband forces raised this turn.
      </p>
    )
  }
  if (actionName === "Select faction leader") {
    return factionLeaderDescription
  }
  if (actionName === "Sponsor games") {
    return (
      <>
        <p>
          Senators may spend talents to sponsor games. These games lower
          Rome&apos;s unrest and increase the sponsor&apos;s popularity.
        </p>
        <div className="flex flex-col gap-2 text-sm">
          <div>
            <p className="mt-1 font-semibold">Slice and dice</p>
            <p>Costs 7 talents, -1 unrest, +1 popularity</p>
          </div>
          <div>
            <p className="mt-1 font-semibold">Blood fest </p>
            <p>Costs 13 talents, -2 unrest, +2 popularity</p>
          </div>
          <div>
            <p className="mt-1 font-semibold">Gladiator gala </p>
            <p>Costs 18 talents, -3 unrest, +3 popularity</p>
          </div>
        </div>
      </>
    )
  }
  if (actionName === "Transfer talents") {
    return <p>Send talents to a senator in another faction.</p>
  }
  if (actionName === "Attack war") {
    return (
      <p>
        Rome is besieged by four or more wars, so you must beat them back below
        four to win. You need enough fleets to meet each war&apos;s fleet
        support, and a victory in every battle. Anything less and every player
        loses.
      </p>
    )
  }
  if (actionName === "Declare civil war") {
    return (
      <p>
        Your commander keeps his army and marches on Rome. He loses his knights,
        his offices and his concessions, earns no more revenue, and must pay 2T
        a turn for every legion that follows him. Every other senator in his
        faction must then choose between him and the Republic. His fleets play
        no part and return to the reserve at once.
      </p>
    )
  }
  if (actionName === "Lay down command") {
    return (
      <p>
        Your commander returns to Rome and his forces to the reserve, giving up
        the chance to revolt this turn.
      </p>
    )
  }
  if (actionName === "Roll for legions") {
    return (
      <>
        <p>
          Before deciding whether to revolt, your commander may test his
          legions. Each rolls one die and follows him on a 5 or 6; those that
          refuse return to the reserve. A talent spent on a legion adds 1 to its
          roll, and only one talent may be spent on each.
        </p>
        <p className="text-sm">
          Veteran legions already loyal to him follow without rolling.
        </p>
        {context.talents !== undefined && (
          <p className="text-sm text-neutral-600">
            {context.talents}T available to spend.
          </p>
        )}
      </>
    )
  }
  if (actionName === "Pay rebel maintenance") {
    return (
      <>
        <p>
          Rebel legions cost 2T each per turn, paid before the redistribution of
          wealth. Veteran legions loyal to a rebel are free. The rest comes from
          the rebel senators&apos; own treasuries unless you draw on the faction
          treasury here.
        </p>
        {context.cost !== undefined && (
          <p className="text-sm text-neutral-600">
            {context.cost}T due for {context.legions} legions.
            {Number(context.must_release) > 0
              ? ` You must release ${context.must_release} of them.`
              : ""}
          </p>
        )}
      </>
    )
  }
  if (actionName === "Pay for released forces") {
    return (
      <p>
        Legions the rebels could not afford have been handed to the Senate. The
        State pays {context.cost}T to keep them, or they are eliminated.
      </p>
    )
  }
  if (actionName === "Refuse released forces") {
    return (
      <p>
        The legions the rebels released are eliminated rather than maintained at
        the State&apos;s expense.
      </p>
    )
  }
  if (actionName === "Play influence peddling") {
    return <p>Steal a random unplayed card from an opponent&apos;s hand.</p>
  }
  return null
}

export default ActionDescription
