import { Tooltip } from "@mui/material"
import ScenarioListItem from "@/components/ScenarioListItem"

const FullListOfWars = () => (
  <div className="flex flex-col gap-4">
    <h5 className="mt-4 font-bold">List of Serial Wars</h5>
    <ul className="flex flex-col gap-0.5">
      <li>
        Illyrian Wars
        <ul>
          <ScenarioListItem scenario="E">
            1<sup>st</sup> Illyrian War
          </ScenarioListItem>
          <ScenarioListItem scenario="E">
            2<sup>nd</sup> Illyrian War
          </ScenarioListItem>
        </ul>
      </li>
      <li>
        Punic Wars
        <ul>
          <ScenarioListItem scenario="E">
            1<sup>st</sup> Punic War
          </ScenarioListItem>
          <ScenarioListItem scenario="E">
            2<sup>nd</sup> Punic War
          </ScenarioListItem>
          <ScenarioListItem scenario="M">
            3<sup>rd</sup> Punic War
          </ScenarioListItem>
          <ScenarioListItem scenario="E">
            <i>Hamilcar (Enemy Leader)</i>
          </ScenarioListItem>
          <ScenarioListItem scenario="E">
            <i>Hannibal (Enemy Leader)</i>
          </ScenarioListItem>
        </ul>
      </li>
      <li>
        Macedonian Wars
        <ul>
          <ScenarioListItem scenario="E">
            1<sup>st</sup> Macedonian War
          </ScenarioListItem>
          <ScenarioListItem scenario="E">
            2<sup>nd</sup> Macedonian War
          </ScenarioListItem>
          <ScenarioListItem scenario="M">
            3<sup>rd</sup> Macedonian War
          </ScenarioListItem>
          <ScenarioListItem scenario="M">
            4<sup>th</sup> Macedonian War
          </ScenarioListItem>
          <ScenarioListItem scenario="E">
            <i>Philip V (Enemy Leader)</i>
          </ScenarioListItem>
        </ul>
      </li>
      <li>
        Spanish Revolts
        <ul>
          <ScenarioListItem scenario="M">Lusitanian War</ScenarioListItem>
          <ScenarioListItem scenario="M">Numantine War</ScenarioListItem>
          <ScenarioListItem scenario="L">Sertorian War</ScenarioListItem>
          <ScenarioListItem scenario="M">
            <i>Viriathus (Enemy Leader)</i>
          </ScenarioListItem>
        </ul>
      </li>
      <li>
        Slave Revolts
        <ul>
          <ScenarioListItem scenario="M">
            1<sup>st</sup> Sicilian Slave Revolt
          </ScenarioListItem>
          <ScenarioListItem scenario="M">
            2<sup>nd</sup> Sicilian Slave Revolt
          </ScenarioListItem>
          <ScenarioListItem scenario="L">Gladiator Revolt</ScenarioListItem>
          <ScenarioListItem scenario="L">
            <i>Spartacus (Enemy Leader)</i>
          </ScenarioListItem>
        </ul>
      </li>
      <li>
        Cilician Pirates
        <ul>
          <ScenarioListItem scenario="M">
            1<sup>st</sup> Cilician Pirates
          </ScenarioListItem>
          <ScenarioListItem scenario="L">
            2<sup>nd</sup> Cilician Pirates
          </ScenarioListItem>
        </ul>
      </li>
      <li>
        Gallic Wars
        <ul>
          <ScenarioListItem scenario="E">
            1<sup>st</sup> Gallic War
          </ScenarioListItem>
          <ScenarioListItem scenario="L">
            2<sup>nd</sup> Gallic War
          </ScenarioListItem>
          <ScenarioListItem scenario="L">
            3<sup>rd</sup> Gallic War
          </ScenarioListItem>
          <ScenarioListItem scenario="L">
            <i>Vercingetorix (Enemy Leader)</i>
          </ScenarioListItem>
        </ul>
      </li>
      <li>
        Mithridatic Wars
        <ul>
          <ScenarioListItem scenario="L">
            1<sup>st</sup> Mithridatic War
          </ScenarioListItem>
          <ScenarioListItem scenario="L">
            2<sup>nd</sup> Mithridatic War
          </ScenarioListItem>
          <ScenarioListItem scenario="L">
            3<sup>rd</sup> Mithridatic War
          </ScenarioListItem>
          <ScenarioListItem scenario="L">
            <i>Mithridates VI (Enemy Leader)</i>
          </ScenarioListItem>
        </ul>
      </li>
    </ul>
    <h5 className="mt-4 font-bold">List of Non-serial Wars</h5>
    <ul className="flex flex-col gap-0.5">
      <li className="text-red-600 dark:text-red-300">
        Syrian War{" "}
        <Tooltip title="Early Republic Scenario" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="E">
            <i>Antiochus III (Enemy Leader)</i>
          </ScenarioListItem>
        </ul>
      </li>
      <ScenarioListItem scenario="M">Germanic Migrations</ScenarioListItem>
      <ScenarioListItem scenario="M">Jugurthine War</ScenarioListItem>
      <ScenarioListItem scenario="L">Social War</ScenarioListItem>
      <ScenarioListItem scenario="L">Invasion of Germania</ScenarioListItem>
      <ScenarioListItem scenario="L">Invasion of Britannia</ScenarioListItem>
      <ScenarioListItem scenario="L">Parthian War</ScenarioListItem>
      <li className="text-blue-600 dark:text-blue-300">
        Alexandrine War{" "}
        <Tooltip title="Late Republic Scenario" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="L">
            <i>Cleopatra VII (Enemy Leader)</i>
          </ScenarioListItem>
        </ul>
      </li>
    </ul>
  </div>
)

export default FullListOfWars
