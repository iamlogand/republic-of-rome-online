import React, { useRef, useEffect, useState, useCallback } from "react"
import Dialog from "@mui/material/Dialog"
import IconButton from "@mui/material/IconButton"
import TextField from "@mui/material/TextField"
import SearchIcon from "@mui/icons-material/Search"
import CloseIcon from "@mui/icons-material/Close"
import { InputAdornment } from "@mui/material"
import termComponents from "@/componentTables/termComponents"
import { useGameContext } from "@/contexts/GameContext"
import TermLink from "./TermLink"

const Search = () => {
  const { dialog, setDialog } = useGameContext()

  const searchInputRef = useRef<HTMLInputElement>(null)
  const [filteredTerms, setFilteredTerms] = useState<string[]>([])
  const [query, setQuery] = useState<string>("")

  const handleQueryChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setQuery(event.target.value)
    },
    []
  )

  // Focus on search input when dialog opens
  useEffect(() => {
    if (searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [dialog])

  // Filter terms based on the query
  useEffect(() => {
    const filteredTerms = Object.keys(termComponents).filter((term) =>
      term.toLowerCase().includes(query.toLowerCase())
    )
    setFilteredTerms(filteredTerms)
  }, [query])

  // Clear query when dialog closes
  useEffect(() => {
    if (dialog !== "search") {
      setQuery("")
    }
  }, [dialog])

  return (
    <>
      <IconButton
        aria-label="debugging tools"
        onClick={() => setDialog("search")}
      >
        <SearchIcon />
      </IconButton>
      <Dialog
        open={dialog === "search"}
        onClose={() => setDialog(null)}
        TransitionProps={{
          onEntered: () => {
            if (searchInputRef.current) {
              searchInputRef.current.focus()
            }
          },
        }}
      >
        <div className="p-6 pb-0 flex items-center gap-4">
          <TextField
            inputRef={searchInputRef}
            type="text"
            name="query"
            value={query}
            onChange={handleQueryChange}
            placeholder="What are you looking for?"
            fullWidth
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </div>
        <div className="absolute right-2 top-2 bg-inherit">
          <IconButton aria-label="close" onClick={() => setDialog(null)}>
            <CloseIcon />
          </IconButton>
        </div>
        <div className="m-6 h-[400px] border border-solid border-neutral-200 rounded shadow-inner overflow-y-scroll overflow-x-auto">
          <div className="m-4 mx-6 box-border flex flex-col items-start gap-3">
            {filteredTerms.map((term, index) => (
              <div
                key={index}
                className="w-full flex items-center justify-between gap-4"
              >
                <span className="w-[300px]">
                  <TermLink name={term} />
                </span>
                <span className="text-neutral-400">Term</span>
              </div>
            ))}
          </div>
        </div>
      </Dialog>
    </>
  )
}

export default Search
