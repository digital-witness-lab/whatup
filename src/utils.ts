export async function sleep (ms: number): Promise<void> {
  return await new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

export function keys<T extends object> (obj: T): Array<keyof T> {
  return Object.keys(obj) as Array<keyof T>
}
