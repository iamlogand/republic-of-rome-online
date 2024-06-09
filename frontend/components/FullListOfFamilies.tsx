import { Tooltip } from "@mui/material"
import EraItem from "@/components/EraItem"

const FullListOfFamilies = () => (
  <div className="flex flex-col gap-4">
    <h5 className="mt-4 font-bold">List of Families and Statesmen</h5>
    <ul className="flex flex-col gap-0.5">
      <EraItem era="E" listItem>Acilius</EraItem>
      <li className="text-red-600 dark:text-red-300">
        Aemilius{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraItem era="E" listItem>
            L. Aemilius Paullus Macedonicus
          </EraItem>
        </ul>
      </li>
      <EraItem era="E" listItem>Aelius</EraItem>
      <EraItem era="E" listItem>Aurelius</EraItem>
      <EraItem era="E" listItem>Calpurnius</EraItem>
      <EraItem era="E" listItem>Claudius</EraItem>
      <li className="text-red-600 dark:text-red-300">
        Cornelius{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraItem era="E" listItem>
            P. Cornelius Scipio Africanus
          </EraItem>
          <EraItem era="M" listItem>
            P. Cornelius Scipio Aemilianus Africanus
          </EraItem>
          <EraItem era="M" listItem>P. Cornelius Sulla</EraItem>
        </ul>
      </li>
      <li className="text-red-600 dark:text-red-300">
        Fabius{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraItem era="E" listItem>
            Q. Fabius Maximus Verrucosus Cunctator
          </EraItem>
        </ul>
      </li>
      <EraItem era="E" listItem>Flaminius</EraItem>
      <li className="text-red-600 dark:text-red-300">
        Fulvius{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraItem era="M" listItem>M. Fulvius Flaccus</EraItem>
        </ul>
      </li>
      <EraItem era="E" listItem>Furius</EraItem>
      <li className="text-red-600 dark:text-red-300">
        Julius{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraItem era="L" listItem>C. Julius Caesar</EraItem>
        </ul>
      </li>
      <EraItem era="E" listItem>Manlius</EraItem>
      <EraItem era="E" listItem>Papirius</EraItem>
      <EraItem era="E" listItem>Plautius</EraItem>
      <li className="text-red-600 dark:text-red-300">
        Quinctius{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraItem era="E" listItem>
            T. Quinctius Flamininus
          </EraItem>
        </ul>
      </li>
      <EraItem era="E" listItem>Sulpicius</EraItem>
      <EraItem era="E" listItem>Terentius</EraItem>
      <EraItem era="E" listItem>Valerius</EraItem>
      <EraItem era="M" listItem>Cassius</EraItem>
      <li className="text-green-600 dark:text-green-300">
        Porcius{" "}
        <Tooltip title="Middle Republic Era" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
        <ul>
          <EraItem era="E" listItem>
            M. Porcius Cato the Elder
          </EraItem>
          <EraItem era="L" listItem>
            M. Porcius Cato the Younger
          </EraItem>
        </ul>
      </li>
      <li className="text-green-600 dark:text-green-300">
        Popillius{" "}
        <Tooltip title="Middle Republic Era" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
        <ul>
          <EraItem era="M" listItem>P. Popillius Laenas</EraItem>
        </ul>
      </li>
      <li className="text-green-600 dark:text-green-300">
        Sempronius{" "}
        <Tooltip title="Middle Republic Era" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
        <ul>
          <EraItem era="M" listItem>
            T. Sempronius Gracchus
          </EraItem>
          <EraItem era="M" listItem>
            C. Sempronius Gracchus
          </EraItem>
        </ul>
      </li>
      <li className="text-green-600 dark:text-green-300">
        Servilius{" "}
        <Tooltip title="Middle Republic Era" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
        <ul>
          <EraItem era="M" listItem>C. Servilius Glaucia</EraItem>
        </ul>
      </li>
      <li className="text-blue-600 dark:text-blue-300">
        Licinius{" "}
        <Tooltip title="Late Republic Era" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <EraItem era="L" listItem>M. Licinius Crassus</EraItem>
          <EraItem era="L" listItem>L. Licinius Lucullus</EraItem>
        </ul>
      </li>
      <li className="text-blue-600 dark:text-blue-300">
        Marius{" "}
        <Tooltip title="Late Republic Era" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <EraItem era="M" listItem>C. Marius</EraItem>
        </ul>
      </li>
      <EraItem era="L" listItem>Octavius</EraItem>
      <li className="text-blue-600 dark:text-blue-300">
        Pompeius{" "}
        <Tooltip title="Late Republic Era" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <EraItem era="L" listItem>Cn. Pompeius Magnus</EraItem>
        </ul>
      </li>
      <li className="text-blue-600 dark:text-blue-300">
        Tullius{" "}
        <Tooltip title="Late Republic Era" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <EraItem era="L" listItem>M. Tullius Cicero</EraItem>
        </ul>
      </li>
    </ul>
  </div>
)

export default FullListOfFamilies
