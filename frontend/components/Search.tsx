import React, { useRef, useEffect, useState, useCallback } from "react"
import Dialog from "@mui/material/Dialog"
import IconButton from "@mui/material/IconButton"
import TextField from "@mui/material/TextField"
import SearchIcon from "@mui/icons-material/Search"
import CloseIcon from "@mui/icons-material/Close"
import { InputAdornment } from "@mui/material"
import termComponents from "@/componentTables/termComponents"
import { useGameContext } from "@/contexts/GameContext"
import SelectedDetail from "@/types/SelectedDetail"
import Senator from "@/classes/Senator"
import { Neutral100 } from "@/themes/colors"
import { useCookieContext } from "@/contexts/CookieContext"

interface SearchResult {
  name: string
  type: string
  id?: number
  sortingName?: string
}

const Search = () => {
  const { darkMode } = useCookieContext()
  const { allSenators, dialog, setDialog, setSelectedDetail } = useGameContext()

  const searchInputRef = useRef<HTMLInputElement>(null)
  const [filteredItems, setFilteredItems] = useState<SearchResult[]>([])
  const [query, setQuery] = useState<string>("")

  // Focus on search input when dialog opens
  useEffect(() => {
    if (searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [dialog])

  // Filter items based on the query
  useEffect(() => {
    const filteredTermItems = Object.keys(termComponents)
      .filter((term) => term.toLowerCase().includes(query.toLowerCase()))
      .map((term) => ({ name: term, type: "Term" }))
    const filteredSenatorItems = allSenators.asArray
      .filter((senator: Senator) =>
        senator.displayName.toLowerCase().includes(query.toLowerCase())
      )
      .map((senator: Senator) => ({
        name: senator.displayName,
        type: "Senator",
        id: senator.id,
        sortingName: senator.name + String(senator.generation).padStart(3, "0"),
      }))
    const filteredItems = filteredTermItems
      .concat(filteredSenatorItems)
      .sort((a: SearchResult, b: SearchResult) =>
        (a.sortingName ?? a.name).localeCompare(b.sortingName ?? b.name)
      )

    setFilteredItems(filteredItems)
  }, [query])

  // Clear query when dialog closes
  useEffect(() => {
    if (dialog !== "search") {
      setQuery("")
    }
  }, [dialog])

  const handleQueryChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setQuery(event.target.value)
    },
    []
  )

  const handleClick = useCallback(
    (
      event: React.MouseEvent<HTMLButtonElement, MouseEvent>,
      item: SearchResult
    ) => {
      event.preventDefault()
      setDialog(null)
      if (item.type === "Term") {
        setSelectedDetail({
          type: "Term",
          name: item.name,
        } as SelectedDetail)
      } else {
        setSelectedDetail({
          type: item.type,
          id: item.id,
        } as SelectedDetail)
      }
    },
    [setDialog, setSelectedDetail]
  )

  return (
    <>
      <button
        aria-label="Search"
        onClick={() => setDialog("search")}
        className={
          "p-2 px-3 border border-solid rounded flex min-w-[140px] items-center \
          text-neutral-500 dark:text-neutral-300 bg-white dark:bg-neutral-650 \
          border-neutral-300 dark:border-neutral-500 hover:border-neutral-400 dark:hover:border-neutral-300"
        }
      >
        <SearchIcon />
        <span className="grow">Search...</span>
      </button>
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
        maxWidth="xs"
        fullWidth
      >
        <div className="absolute right-2 top-2 bg-inherit z-10">
          <IconButton aria-label="close" onClick={() => setDialog(null)}>
            <CloseIcon />
          </IconButton>
        </div>
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
                  <SearchIcon sx={darkMode ? { color: Neutral100 } : {}} />
                </InputAdornment>
              ),
              autoComplete: "off",
            }}
          />
        </div>
        <div
          className={
            "m-6 h-[400px] border border-solid rounded shadow-inner overflow-y-scroll overflow-x-auto\
            border-neutral-200 dark:border-neutral-750 dark:bg-neutral-650"
          }
        >
          {filteredItems.length > 0 ? (
            <ul className="list-none p-0 m-2 box-border flex flex-col items-start gap-2">
              {filteredItems.map((item: SearchResult, index: number) => (
                <li key={index} className="w-full">
                  <button
                    onClick={(
                      event: React.MouseEvent<HTMLButtonElement, MouseEvent>
                    ) => handleClick(event, item)}
                    className={
                      "w-full px-4 py-2.5 rounded border-none flex items-center justify-between gap-4 \
                      bg-neutral-100 dark:bg-neutral-700 hover:text-white dark:hover:text-black hover:bg-tyrian-700 dark:hover:bg-tyrian-300"
                    }
                  >
                    <span>{item.name}</span>
                    <span className="grow text-sm flex justify-end">
                      {item.type}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="flex items-center justify-center h-[100px]">
              <span className="text-neutral-500 dark:text-neutral-200">
                No results for "
                <span className="text-tyrian-600 dark:text-tyrian-200 text-lg">
                  {query}
                </span>
                "
              </span>
            </div>
          )}
        </div>
      </Dialog>
    </>
  )
}

export default Search
