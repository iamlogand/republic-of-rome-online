import { Tooltip } from "@mui/material"
import EraListItem from "@/components/EraListItem"

const FullListOfFamilies = () => (
  <div className="flex flex-col gap-4">
    <h5 className="mt-4 font-bold">List of Families and Statesmen</h5>
    <ul className="flex flex-col gap-0.5">
      <EraListItem era="E">Acilius</EraListItem>
      <li className="text-red-600 dark:text-red-300">
        Aemilius{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraListItem era="E">
            L. Aemilius Paullus Macedonicus
          </EraListItem>
        </ul>
      </li>
      <EraListItem era="E">Aelius</EraListItem>
      <EraListItem era="E">Aurelius</EraListItem>
      <EraListItem era="E">Calpurnius</EraListItem>
      <EraListItem era="E">Claudius</EraListItem>
      <li className="text-red-600 dark:text-red-300">
        Cornelius{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraListItem era="E">
            P. Cornelius Scipio Africanus
          </EraListItem>
          <EraListItem era="M">
            P. Cornelius Scipio Aemilianus Africanus
          </EraListItem>
          <EraListItem era="M">P. Cornelius Sulla</EraListItem>
        </ul>
      </li>
      <li className="text-red-600 dark:text-red-300">
        Fabius{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraListItem era="E">
            Q. Fabius Maximus Verrucosus Cunctator
          </EraListItem>
        </ul>
      </li>
      <EraListItem era="E">Flaminius</EraListItem>
      <li className="text-red-600 dark:text-red-300">
        Fulvius{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraListItem era="M">M. Fulvius Flaccus</EraListItem>
        </ul>
      </li>
      <EraListItem era="E">Furius</EraListItem>
      <li className="text-red-600 dark:text-red-300">
        Julius{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraListItem era="L">C. Julius Caesar</EraListItem>
        </ul>
      </li>
      <EraListItem era="E">Manlius</EraListItem>
      <EraListItem era="E">Papirius</EraListItem>
      <EraListItem era="E">Plautius</EraListItem>
      <li className="text-red-600 dark:text-red-300">
        Quinctius{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraListItem era="E">
            T. Quinctius Flamininus
          </EraListItem>
        </ul>
      </li>
      <EraListItem era="E">Sulpicius</EraListItem>
      <EraListItem era="E">Terentius</EraListItem>
      <EraListItem era="E">Valerius</EraListItem>
      <EraListItem era="M">Cassius</EraListItem>
      <li className="text-green-600 dark:text-green-300">
        Porcius{" "}
        <Tooltip title="Middle Republic Era" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
        <ul>
          <EraListItem era="E">
            M. Porcius Cato the Elder
          </EraListItem>
          <EraListItem era="L">
            M. Porcius Cato the Younger
          </EraListItem>
        </ul>
      </li>
      <li className="text-green-600 dark:text-green-300">
        Popillius{" "}
        <Tooltip title="Middle Republic Era" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
        <ul>
          <EraListItem era="M">P. Popillius Laenas</EraListItem>
        </ul>
      </li>
      <li className="text-green-600 dark:text-green-300">
        Sempronius{" "}
        <Tooltip title="Middle Republic Era" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
        <ul>
          <EraListItem era="M">
            T. Sempronius Gracchus
          </EraListItem>
          <EraListItem era="M">
            C. Sempronius Gracchus
          </EraListItem>
        </ul>
      </li>
      <li className="text-green-600 dark:text-green-300">
        Servilius{" "}
        <Tooltip title="Middle Republic Era" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
        <ul>
          <EraListItem era="M">C. Servilius Glaucia</EraListItem>
        </ul>
      </li>
      <li className="text-blue-600 dark:text-blue-300">
        Licinius{" "}
        <Tooltip title="Late Republic Era" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <EraListItem era="L">M. Licinius Crassus</EraListItem>
          <EraListItem era="L">L. Licinius Lucullus</EraListItem>
        </ul>
      </li>
      <li className="text-blue-600 dark:text-blue-300">
        Marius{" "}
        <Tooltip title="Late Republic Era" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <EraListItem era="M">C. Marius</EraListItem>
        </ul>
      </li>
      <EraListItem era="L">Octavius</EraListItem>
      <li className="text-blue-600 dark:text-blue-300">
        Pompeius{" "}
        <Tooltip title="Late Republic Era" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <EraListItem era="L">Cn. Pompeius Magnus</EraListItem>
        </ul>
      </li>
      <li className="text-blue-600 dark:text-blue-300">
        Tullius{" "}
        <Tooltip title="Late Republic Era" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <EraListItem era="L">M. Tullius Cicero</EraListItem>
        </ul>
      </li>
    </ul>
  </div>
)

export default FullListOfFamilies
