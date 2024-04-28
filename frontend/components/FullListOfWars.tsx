import { Tooltip } from "@mui/material"
import EraListItem from "@/components/EraListItem"

const FullListOfWars = () => (
  <div className="flex flex-col gap-4">
    <h5 className="mt-4 font-bold">List of Wars and Enemy Leaders</h5>
    <ul className="flex flex-col gap-0.5">
      <li>
        Illyrian Wars
        <ul>
          <EraListItem era="E">
            1<sup>st</sup> Illyrian War
          </EraListItem>
          <EraListItem era="E">
            2<sup>nd</sup> Illyrian War
          </EraListItem>
        </ul>
      </li>
      <li>
        Punic Wars
        <ul>
          <EraListItem era="E">
            1<sup>st</sup> Punic War
          </EraListItem>
          <EraListItem era="E">
            2<sup>nd</sup> Punic War
          </EraListItem>
          <EraListItem era="M">
            3<sup>rd</sup> Punic War
          </EraListItem>
          <EraListItem era="E">
            <i>Hamilcar (Enemy Leader)</i>
          </EraListItem>
          <EraListItem era="E">
            <i>Hannibal (Enemy Leader)</i>
          </EraListItem>
        </ul>
      </li>
      <li>
        Macedonian Wars
        <ul>
          <EraListItem era="E">
            1<sup>st</sup> Macedonian War
          </EraListItem>
          <EraListItem era="E">
            2<sup>nd</sup> Macedonian War
          </EraListItem>
          <EraListItem era="M">
            3<sup>rd</sup> Macedonian War
          </EraListItem>
          <EraListItem era="M">
            4<sup>th</sup> Macedonian War
          </EraListItem>
          <EraListItem era="E">
            <i>Philip V (Enemy Leader)</i>
          </EraListItem>
        </ul>
      </li>
      <li className="text-red-600 dark:text-red-300">
        Syrian War{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
        <ul>
          <EraListItem era="E">
            <i>Antiochus III (Enemy Leader)</i>
          </EraListItem>
        </ul>
      </li>
      <li>
        Spanish Revolts
        <ul>
          <EraListItem era="M">Lusitanian War</EraListItem>
          <EraListItem era="M">Numantine War</EraListItem>
          <EraListItem era="L">Sertorian War</EraListItem>
          <EraListItem era="M">
            <i>Viriathus (Enemy Leader)</i>
          </EraListItem>
        </ul>
      </li>
      <li>
        Slave Revolts
        <ul>
          <EraListItem era="M">
            1<sup>st</sup> Sicilian Slave Revolt
          </EraListItem>
          <EraListItem era="M">
            2<sup>nd</sup> Sicilian Slave Revolt
          </EraListItem>
          <EraListItem era="L">Gladiator Revolt</EraListItem>
          <EraListItem era="L">
            <i>Spartacus (Enemy Leader)</i>
          </EraListItem>
        </ul>
      </li>
      <EraListItem era="M">Germanic Migrations</EraListItem>
      <EraListItem era="M">Jugurthine War</EraListItem>
      <li>
        Cilician Pirates
        <ul>
          <EraListItem era="M">
            1<sup>st</sup> Cilician Pirates
          </EraListItem>
          <EraListItem era="L">
            2<sup>nd</sup> Cilician Pirates
          </EraListItem>
        </ul>
      </li>
      <li>
        Gallic Wars
        <ul>
          <EraListItem era="E">
            1<sup>st</sup> Gallic War
          </EraListItem>
          <EraListItem era="L">
            2<sup>nd</sup> Gallic War
          </EraListItem>
          <EraListItem era="L">
            3<sup>rd</sup> Gallic War
          </EraListItem>
          <EraListItem era="L">
            <i>Vercingetorix (Enemy Leader)</i>
          </EraListItem>
        </ul>
      </li>
      <EraListItem era="L">Social War</EraListItem>
      <li>
        Mithridatic Wars
        <ul>
          <EraListItem era="L">
            1<sup>st</sup> Mithridatic War
          </EraListItem>
          <EraListItem era="L">
            2<sup>nd</sup> Mithridatic War
          </EraListItem>
          <EraListItem era="L">
            3<sup>rd</sup> Mithridatic War
          </EraListItem>
          <EraListItem era="L">
            <i>Mithridates VI (Enemy Leader)</i>
          </EraListItem>
        </ul>
      </li>
      <EraListItem era="L">Invasion of Germania</EraListItem>
      <EraListItem era="L">Invasion of Britannia</EraListItem>
      <EraListItem era="L">Parthian War</EraListItem>
      <li className="text-blue-600 dark:text-blue-300">
        Alexandrine War{" "}
        <Tooltip title="Late Republic Era" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
        <ul>
          <EraListItem era="L">
            <i>Cleopatra VII (Enemy Leader)</i>
          </EraListItem>
        </ul>
      </li>
    </ul>
  </div>
)

export default FullListOfWars
