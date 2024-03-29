import { Tooltip } from "@mui/material"
import ScenarioListItem from "@/components/ScenarioListItem"

const FullListOfFamilies = () => (
  <div className="flex flex-col gap-4">
    <h5 className="mt-4 font-bold">List of Families and Statesmen</h5>
    <ul className="flex flex-col gap-0.5">
      <ScenarioListItem scenario="E">Acilius</ScenarioListItem>
      <li className="text-red-600 dark:text-red-300">
        Aemilius{" "}
        <Tooltip title="Late Republic Scenario" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="E">
            L. Aemilius Paullus Macedonicus
          </ScenarioListItem>
        </ul>
      </li>
      <ScenarioListItem scenario="E">Aelius</ScenarioListItem>
      <ScenarioListItem scenario="E">Aurelius</ScenarioListItem>
      <ScenarioListItem scenario="E">Calpurnius</ScenarioListItem>
      <ScenarioListItem scenario="E">Claudius</ScenarioListItem>
      <li className="text-red-600 dark:text-red-300">
        Cornelius{" "}
        <Tooltip title="Late Republic Scenario" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="E">
            P. Cornelius Scipio Africanus
          </ScenarioListItem>
          <ScenarioListItem scenario="M">
            P. Cornelius Scipio Aemilianus Africanus
          </ScenarioListItem>
          <ScenarioListItem scenario="M">P. Cornelius Sulla</ScenarioListItem>
        </ul>
      </li>
      <li className="text-red-600 dark:text-red-300">
        Fabius{" "}
        <Tooltip title="Late Republic Scenario" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="E">
            Q. Fabius Maximus Verrucosus Cunctator
          </ScenarioListItem>
        </ul>
      </li>
      <ScenarioListItem scenario="E">Flaminius</ScenarioListItem>
      <li className="text-red-600 dark:text-red-300">
        Fulvius{" "}
        <Tooltip title="Late Republic Scenario" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="M">M. Fulvius Flaccus</ScenarioListItem>
        </ul>
      </li>
      <ScenarioListItem scenario="E">Furius</ScenarioListItem>
      <li className="text-red-600 dark:text-red-300">
        Julius{" "}
        <Tooltip title="Early Republic Scenario" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="L">C. Julius Caesar</ScenarioListItem>
        </ul>
      </li>
      <ScenarioListItem scenario="E">Manlius</ScenarioListItem>
      <ScenarioListItem scenario="E">Papirius</ScenarioListItem>
      <ScenarioListItem scenario="E">Plautius</ScenarioListItem>
      <li className="text-red-600 dark:text-red-300">
        Quinctius{" "}
        <Tooltip title="Late Republic Scenario" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="E">
            T. Quinctius Flamininus
          </ScenarioListItem>
        </ul>
      </li>
      <ScenarioListItem scenario="E">Sulpicius</ScenarioListItem>
      <ScenarioListItem scenario="E">Terentius</ScenarioListItem>
      <ScenarioListItem scenario="E">Valerius</ScenarioListItem>
      <ScenarioListItem scenario="M">Cassius</ScenarioListItem>
      <li className="text-green-600 dark:text-green-300">
        Porcius{" "}
        <Tooltip title="Middle Republic Scenario" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="E">
            M. Porcius Cato the Elder
          </ScenarioListItem>
          <ScenarioListItem scenario="L">
            M. Porcius Cato the Younger
          </ScenarioListItem>
        </ul>
      </li>
      <li className="text-green-600 dark:text-green-300">
        Popillius{" "}
        <Tooltip title="Middle Republic Scenario" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="M">P. Popillius Laenas</ScenarioListItem>
        </ul>
      </li>
      <li className="text-green-600 dark:text-green-300">
        Sempronius{" "}
        <Tooltip title="Middle Republic Scenario" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="M">
            T. Sempronius Gracchus
          </ScenarioListItem>
          <ScenarioListItem scenario="M">
            C. Sempronius Gracchus
          </ScenarioListItem>
        </ul>
      </li>
      <li className="text-green-600 dark:text-green-300">
        Servilius{" "}
        <Tooltip title="Middle Republic Scenario" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="M">C. Servilius Glaucia</ScenarioListItem>
        </ul>
      </li>
      <li className="text-blue-600 dark:text-blue-300">
        Licinius{" "}
        <Tooltip title="Late Republic Scenario" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="L">M. Licinius Crassus</ScenarioListItem>
          <ScenarioListItem scenario="L">L. Licinius Lucullus</ScenarioListItem>
        </ul>
      </li>
      <li className="text-blue-600 dark:text-blue-300">
        Marius{" "}
        <Tooltip title="Late Republic Scenario" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="M">C. Marius</ScenarioListItem>
        </ul>
      </li>
      <ScenarioListItem scenario="L">Octavius</ScenarioListItem>
      <li className="text-blue-600 dark:text-blue-300">
        Pompeius{" "}
        <Tooltip title="Late Republic Scenario" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="L">Cn. Pompeius Magnus</ScenarioListItem>
        </ul>
      </li>
      <li className="text-blue-600 dark:text-blue-300">
        Tullius{" "}
        <Tooltip title="Late Republic Scenario" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <ScenarioListItem scenario="L">M. Tullius Cicero</ScenarioListItem>
        </ul>
      </li>
    </ul>
  </div>
)

export default FullListOfFamilies
