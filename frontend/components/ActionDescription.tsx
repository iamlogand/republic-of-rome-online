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
  if (actionName === "Elect Censor") {
    return (
      <p>
        The Censor oversees prosecutions of corrupt senators. Candidates must be
        prior consuls. The current Censor is eligible for re-election.
      </p>
    )
  }
  if (actionName === "Elect consuls") {
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
        Raising a legion or fleet costs the State 10T, with a maintenance cost
        of 2T per turn.
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
  return null
}

export default ActionDescription
