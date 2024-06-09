import { Tooltip } from "@mui/material"
import EraItem from "@/components/EraItem"

const FullListOfWars = () => (
  <div className="flex flex-col gap-4">
    <h5 className="mt-4 font-bold">List of Wars and Enemy Leaders</h5>
    <ul className="flex flex-col gap-0.5">
      <li>
        Illyrian Wars
        <ul>
          <EraItem
            era="E"
            name={
              <>
                1<sup>st</sup> Illyrian War
              </>
            }
            listItem
          />
          <EraItem
            era="E"
            name={
              <>
                2<sup>nd</sup> Illyrian War
              </>
            }
            listItem
          />
        </ul>
      </li>
      <li>
        Punic Wars
        <ul>
          <EraItem
            era="E"
            name={
              <>
                1<sup>st</sup> Punic War
              </>
            }
            listItem
          />
          <EraItem
            era="E"
            name={
              <>
                2<sup>nd</sup> Punic War
              </>
            }
            listItem
          />
          <EraItem
            era="M"
            name={
              <>
                3<sup>rd</sup> Punic War
              </>
            }
            listItem
          />
          <EraItem era="E" name={<>Hamilcar</>} enemyLeader listItem />
          <EraItem era="E" name={<>Hannibal</>} enemyLeader listItem />
        </ul>
      </li>
      <li>
        Macedonian Wars
        <ul>
          <EraItem
            era="E"
            name={
              <>
                1<sup>st</sup> Macedonian War
              </>
            }
            listItem
          />
          <EraItem
            era="E"
            name={
              <>
                2<sup>nd</sup> Macedonian War
              </>
            }
            listItem
          />
          <EraItem
            era="M"
            name={
              <>
                3<sup>rd</sup> Macedonian War
              </>
            }
            listItem
          />
          <EraItem
            era="M"
            name={
              <>
                4<sup>th</sup> Macedonian War
              </>
            }
            listItem
          />
          <EraItem era="E" name={<>Philip V</>} enemyLeader listItem />
        </ul>
      </li>
      <EraItem
        era="E"
        name="Syrian War"
        childList={
          <EraItem era="E" name={<>Antiochus III</>} enemyLeader listItem />
        }
        listItem
      ></EraItem>
      <li>
        Spanish Revolts
        <ul>
          <EraItem era="M" name={<>Lusitanian War</>} listItem />
          <EraItem era="M" name={<>Numantine War</>} listItem />
          <EraItem era="L" name={<>Sertorian War</>} listItem />
          <EraItem era="M" name={<>Viriathus</>} enemyLeader listItem />
        </ul>
      </li>
      <li>
        Slave Revolts
        <ul>
          <EraItem
            era="M"
            name={
              <>
                1<sup>st</sup> Sicilian Slave Revolt
              </>
            }
            listItem
          />
          <EraItem
            era="M"
            name={
              <>
                2<sup>nd</sup> Sicilian Slave Revolt
              </>
            }
            listItem
          />
          <EraItem era="L" name={<>Gladiator Revolt</>} listItem />
          <EraItem era="L" name={<>Spartacus</>} enemyLeader listItem />
        </ul>
      </li>
      <EraItem era="M" name={<>Germanic Migrations</>} listItem />
      <EraItem era="M" name={<>Jugurthine War</>} listItem />
      <li>
        Cilician Pirates
        <ul>
          <EraItem
            era="M"
            name={
              <>
                1<sup>st</sup> Cilician Pirates
              </>
            }
            listItem
          />
          <EraItem
            era="L"
            name={
              <>
                2<sup>nd</sup> Cilician Pirates
              </>
            }
            listItem
          />
        </ul>
      </li>
      <li>
        Gallic Wars
        <ul>
          <EraItem
            era="E"
            name={
              <>
                1<sup>st</sup> Gallic War
              </>
            }
            listItem
          />
          <EraItem
            era="L"
            name={
              <>
                2<sup>nd</sup> Gallic War
              </>
            }
            listItem
          />
          <EraItem
            era="L"
            name={
              <>
                3<sup>rd</sup> Gallic War
              </>
            }
            listItem
          />
          <EraItem era="L" name={<>Vercingetorix</>} enemyLeader listItem />
        </ul>
      </li>
      <EraItem era="L" name={<>Social War</>} listItem />
      <li>
        Mithridatic Wars
        <ul>
          <EraItem
            era="L"
            name={
              <>
                1<sup>st</sup> Mithridatic War
              </>
            }
            listItem
          />
          <EraItem
            era="L"
            name={
              <>
                2<sup>nd</sup> Mithridatic War
              </>
            }
            listItem
          />
          <EraItem
            era="L"
            name={
              <>
                3<sup>rd</sup> Mithridatic War
              </>
            }
            listItem
          />
          <EraItem era="L" name={<>Mithridates VI</>} enemyLeader listItem />
        </ul>
      </li>
      <EraItem era="L" name={<>Invasion of Germania</>} listItem />
      <EraItem era="L" name={<>Invasion of Britannia</>} listItem />
      <EraItem era="L" name={<>Parthian War</>} listItem />
      <EraItem
        era="L"
        name={<>Alexandrine War</>}
        childList={
          <EraItem era="L" name={<>Cleopatra VII</>} enemyLeader listItem />
        }
        listItem
      />
    </ul>
  </div>
)

export default FullListOfWars
