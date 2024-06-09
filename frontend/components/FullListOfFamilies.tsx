import EraItem from "@/components/EraItem"

const FullListOfFamilies = () => (
  <div className="flex flex-col gap-4">
    <h5 className="mt-4 font-bold">List of Families and Statesmen</h5>
    <ul className="flex flex-col gap-0.5">
      <EraItem era="E" name="Acilius" listItem />
      <EraItem
        era="E"
        name="Aemilius"
        childList={
          <EraItem era="E" name="L. Aemilius Paullus Macedonicus" listItem />
        }
        listItem
      />
      <EraItem era="E" name="Aelius" listItem />
      <EraItem era="E" name="Aurelius" listItem />
      <EraItem era="E" name="Calpurnius" listItem />
      <EraItem era="E" name="Claudius" listItem />
      <EraItem
        era="E"
        name="Cornelius"
        childList={
          <>
            <EraItem era="E" name="P. Cornelius Scipio Africanus" listItem />
            <EraItem
              era="M"
              name="P. Cornelius Scipio Aemilianus Africanus"
              listItem
            />
            <EraItem era="M" name="P. Cornelius Sulla" listItem />
          </>
        }
        listItem
      />
      <EraItem
        era="E"
        name="Fabius"
        childList={
          <EraItem
            era="E"
            name="Q. Fabius Maximus Verrucosus Cunctator"
            listItem
          />
        }
        listItem
      />
      <EraItem era="E" name="Flaminius" listItem />
      <EraItem
        era="E"
        name="Fulvius"
        childList={<EraItem era="M" name="M. Fulvius Flaccus" listItem />}
        listItem
      />
      <EraItem era="E" name="Furius" listItem />
      <EraItem
        era="E"
        name="Julius"
        childList={<EraItem era="L" name="C. Julius Caesar" listItem />}
        listItem
      />
      <EraItem era="E" name="Manlius" listItem />
      <EraItem era="E" name="Papirius" listItem />
      <EraItem era="E" name="Plautius" listItem />
      <EraItem
        era="E"
        name="Quinctius"
        childList={<EraItem era="E" name="T. Quinctius Flamininus" listItem />}
        listItem
      />
      <EraItem era="E" name="Sulpicius" listItem />
      <EraItem era="E" name="Terentius" listItem />
      <EraItem era="E" name="Valerius" listItem />
      <EraItem era="M" name="Cassius" listItem />
      <EraItem
        era="M"
        name="Porcius"
        childList={
          <>
            <EraItem era="E" name="M. Porcius Cato the Elder" listItem />
            <EraItem era="L" name="M. Porcius Cato the Younger" listItem />
          </>
        }
        listItem
      />
      <EraItem
        era="M"
        name="Popillius"
        childList={<EraItem era="M" name="P. Popillius Laenas" listItem />}
        listItem
      />
      <EraItem
        era="M"
        name="Sempronius"
        childList={
          <>
            <EraItem era="M" name="T. Sempronius Gracchus" listItem />
            <EraItem era="M" name="C. Sempronius Gracchus" listItem />
          </>
        }
        listItem
      />
      <EraItem
        era="M"
        name="Servilius"
        childList={<EraItem era="M" name="C. Servilius Glaucia" listItem />}
        listItem
      />
      <EraItem
        era="L"
        name="Licinius"
        childList={
          <>
            <EraItem era="L" name="M. Licinius Crassus" listItem />
            <EraItem era="L" name="L. Licinius Lucullus" listItem />
          </>
        }
        listItem
      />
      <EraItem
        era="L"
        name="Marius"
        childList={<EraItem era="M" name="C. Marius" listItem />}
        listItem
      />
      <EraItem era="L" name="Octavius" listItem />
      <EraItem
        era="L"
        name="Pompeius"
        childList={<EraItem era="L" name="Cn. Pompeius Magnus" listItem />}
        listItem
      />
      <EraItem
        era="L"
        name="Tullius"
        childList={<EraItem era="L" name="M. Tullius Cicero" listItem />}
        listItem
      />
    </ul>
  </div>
)

export default FullListOfFamilies
