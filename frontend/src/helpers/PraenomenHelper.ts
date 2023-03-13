import Praenomen from "../types/Praenomen";

const abbreviations = {
    "gaius": "c",
    "lucius": "l",
    "quintus": "q",
    "titus": "t"
}

const getPraenomenAbbr = (praenomen: Praenomen) => {
    return abbreviations[praenomen] + "."
}

export default getPraenomenAbbr;