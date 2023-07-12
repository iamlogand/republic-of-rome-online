/**
 * Deserialize a JSON string or an object into an instance of a specified class
 * @param constructor the class constructor
 * @param data the data to deserialize (can be a JSON string or a generic object)
 * @returns an instance of the specified class, or undefined if deserialization fails
 */
export const deserializeToInstance = <T>(
  constructor: new (o: any) => T,
  data: string | Record<string, unknown>
): T | undefined => {
  let deserializedData;
  if (typeof data === 'string') {
    try {
      deserializedData = JSON.parse(data);
    } catch {
      return undefined;
    }
  } else if (typeof data === 'object' && data !== null) {
    deserializedData = data;
  } else {
    return undefined;
  }
  return new constructor(deserializedData);
}

/**
 * Deserialize a JSON string representing an array or an array of objects into instances of a specified class
 * @param constructor the class constructor
 * @param dataList the list of data to deserialize (each can be a JSON string representing an array or a generic object)
 * @returns a list of instances of the specified class, or an empty list if deserialization fails
 */
export const deserializeToInstances = <T>(
  constructor: new (o: any) => T,
  dataList: string | Array<Record<string, unknown>>
): Array<T> => {
  let deserializedDataList: Array<Record<string, unknown>>;

  if (typeof dataList === 'string') {
    try {
      deserializedDataList = JSON.parse(dataList);
      if (!Array.isArray(deserializedDataList)) {
        return [];
      }
    } catch {
      return [];
    }
  } else {
    deserializedDataList = dataList;
  }

  return deserializedDataList
    .map(data => deserializeToInstance(constructor, data))
    .filter((instance): instance is T => instance !== undefined);
}
