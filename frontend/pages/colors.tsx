import { Button, Link } from "@mui/material"

const ColorsPage = () => {
  const getColorBar = (colorName: string, title: string) => {
    return (
      <div className="grid grid-rows-[repeat(12,_1fr)] items-stretch text-center">
        <div className={`bg-${colorName}-500 p-1`}>
          <p className="m-0">{colorName.toUpperCase()}</p>
          <p className="m-0">{title}</p>
        </div>
        <div className={`bg-${colorName}-50 flex-1`}>50</div>
        <div className={`bg-${colorName}-100 flex-1`}>100</div>
        <div className={`bg-${colorName}-200 flex-1`}>200</div>
        <div className={`bg-${colorName}-300 flex-1`}>300</div>
        <div className={`bg-${colorName}-400 flex-1`}>400</div>
        <div className={`bg-${colorName}-500 flex-1`}>500</div>
        <div className={`bg-${colorName}-600 flex-1`}>600</div>
        <div className={`bg-${colorName}-700 flex-1`}>700</div>
        <div className={`bg-${colorName}-800 flex-1`}>800</div>
        <div className={`bg-${colorName}-900 flex-1`}>900</div>
        <div className={`bg-${colorName}-950 flex-1`}>950</div>
      </div>
    )
  }

  return (
    <main className="standard-page flex flex-col mt-4 gap-4">
      <div className="h-screen w-full grid grid-cols-[repeat(10,_1fr)] align-center text-black">
        {getColorBar("red", "Faction 1 / Error")}
        {getColorBar("orange", "Faction 5 / Warning")}
        {getColorBar("yellow", "Faction 4")}
        {getColorBar("green", "Faction 3 / Success")}
        {getColorBar("blue", "Faction 2")}
        {getColorBar("purple", "Faction 6")}
        {getColorBar("tyrian", "Primary")}
        {getColorBar("stone", "Neutral / Secondary")}
        {getColorBar("teal", "Info")}
        <div className="flex-1 flex flex-col h-[] text-center">
          <div className="bg-white flex-1 p-1">WHITE</div>
          <div className="bg-black flex-1 p-1 text-white">BLACK</div>
        </div>
      </div>
      <div className="flex gap-4">
        <Button variant="contained">Primary</Button>
        <Button variant="outlined">Primary</Button>
        <Button>Primary</Button>
      </div>
      <div className="flex gap-4">
        <Button color="secondary" variant="contained">
          Secondary
        </Button>
        <Button color="secondary" variant="outlined">
          Secondary
        </Button>
        <Button color="secondary">Secondary</Button>
      </div>
      <div className="flex gap-4">
        <Button color="error" variant="contained">
          Error
        </Button>
        <Button color="error" variant="outlined">
          Error
        </Button>
        <Button color="error">Error</Button>
      </div>
      <div className="flex gap-4">
        <Button color="warning" variant="contained">
          Warning
        </Button>
        <Button color="warning" variant="outlined">
          Warning
        </Button>
        <Button color="warning">Warning</Button>
      </div>
      <div className="flex gap-4">
        <Button color="info" variant="contained">
          Info
        </Button>
        <Button color="info" variant="outlined">
          Info
        </Button>
        <Button color="info">Info</Button>
      </div>
      <div className="flex gap-4">
        <Button color="success" variant="contained">
          Success
        </Button>
        <Button color="success" variant="outlined">
          Success
        </Button>
        <Button color="success">Success</Button>
      </div>
      <div className="flex gap-4">
        <Button variant="contained" disabled>
          Disabled
        </Button>
        <Button variant="outlined" disabled>
          Disabled
        </Button>
        <Button disabled>Disabled</Button>
      </div>
      <p>
        Aemilius now holds the position of <Link>Red Faction</Link> Leader,
        taking over from <Link>Fulvius</Link>.
      </p>
    </main>
  )
}

export default ColorsPage
