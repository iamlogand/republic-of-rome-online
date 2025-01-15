"use client"

import { useAppContext } from "@/contexts/AppContext"

const AccountPage = () => {
  const { user } = useAppContext()

  return (
    <div className="px-6 py-4 max-w-[800px]">
      <h1 className="text-lg font-bold mb-4">Account</h1>
      {user && (
        <>
          <p>
            <span className="inline-block w-[100px]">First name:</span>{" "}
            {user.firstName}
          </p>
          <p>
            <span className="inline-block w-[100px]">Last name:</span>{" "}
            {user.lastName}
          </p>
          <p>
            <span className="inline-block w-[100px]">Email:</span> {user.email}
          </p>
        </>
      )}
    </div>
  )
}

export default AccountPage
