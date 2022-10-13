export async function sleep (ms: number): Promise<void> {
  return await new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

export function keys<T extends object> (obj: T): Array<keyof T> {
  return Object.keys(obj) as Array<keyof T>
}

export function resolvePromiseSync (asyncFunc: (...args: any[]) => Promise<void>): () => void {
  return (...args) => {
    asyncFunc(...args).then(() => {}).catch((reason) => { console.log(`Promise failed with reason: ${String(reason)}`) })
  }
}
