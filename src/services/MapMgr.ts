const RADAR_URL = 'https://radar.zeldamods.org';

export type Vec3 = [number, number, number];

export interface ResPlacementObj {
  readonly '!Parameters'?: {[key: string]: any};
  readonly SRTHash: number;
  readonly HashId: number;
  readonly OnlyOne?: boolean;
  readonly UniqueName?: string;
  readonly UnitConfigName: string;
  readonly LinksToObj?: any;
  readonly LinksToRail?: any;
  readonly Translate: Vec3;
  readonly Scale?: Vec3 | number;
  readonly Rotate?: Vec3 | number;
}

export const enum ObjectDropType {
  Actor = 1,
  Table = 2,
}

export interface ObjectMinData {
  objid: number;
  map_name?: string;
  name: string;
  drop?: [ObjectDropType, string];
  equip?: string[];
  pos: [number, number];

  // False if not present.
  hard_mode?: boolean;
  disable_rankup_for_hard_mode?: boolean;

  // Only for LocationTags.
  messageid?: string;

  // Only for weapons and enemies.
  scale?: number;
  sharp_weapon_judge_type?: number;
}

export interface ObjectData extends ObjectMinData {
  map_type: string;
  map_name: string;
  hash_id: number;
  data: ResPlacementObj;
}

export class PlacementLink {
  constructor(public readonly otherObj: ObjectData,
              public readonly linkIter: any,
              public readonly ltype: string,
  ) {}
}

function parse(r: Response) {
  return r.json().then(d => Object.freeze(d));
}

export class MapMgr {
  private static instance: MapMgr;
  static getInstance() {
    if (!this.instance)
      this.instance = new this();
    return this.instance;
  }

  private infoMainField: any;

  async init() {
    await Promise.all([
      fetch('/game_files/map_summary/MainField/static.json').then(r => r.json())
          .then((d) => this.infoMainField = Object.freeze(d)),
    ]);
  }

  getInfoMainField() {
    return this.infoMainField;
  }

  getObjByObjId(objid: number): Promise<ObjectData> {
    return fetch(`${RADAR_URL}/obj/${objid}`).then(parse);
  }
  getObj(mapType: string, mapName: string, hashId: number): Promise<ObjectData> {
    return fetch(`${RADAR_URL}/obj/${mapType}/${mapName}/${hashId}`).then(parse);
  }

  getObjGenGroup(mapType: string, mapName: string, hashId: number): Promise<ObjectData[]> {
    return fetch(`${RADAR_URL}/obj/${mapType}/${mapName}/${hashId}/gen_group`).then(parse);
  }

  getObjs(mapType: string, mapName: string, query: string, withMapNames = false, limit = -1): Promise<ObjectMinData[]> {
    let url = new URL(`${RADAR_URL}/objs/${mapType}/${mapName}`);
    url.search = new URLSearchParams({
      q: query,
      withMapNames: withMapNames.toString(),
      limit: limit.toString(),
    }).toString();
    return fetch(url.toString()).then(parse);
  }

  getObjids(mapType: string, mapName: string, query: string): Promise<number[]> {
    let url = new URL(`${RADAR_URL}/objids/${mapType}/${mapName}`);
    url.search = new URLSearchParams({
      q: query,
    }).toString();
    return fetch(url.toString()).then(parse);
  }
}
