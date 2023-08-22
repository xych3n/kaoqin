export interface BearerToken {
  access_token: string;
  token_type: 'bearer';
}

export interface Pagination<T> {
  total: number;
  list: T[];
}

export interface User {
  id: number,
  student_number: string;
  // id_number: string;
  name: string;
  is_superuser: boolean;
}

type ActivityCategory = '学术讲座' | '研会活动';

export interface UserDetail extends User {
  involvements: {'学术讲座': number, '研会活动': number};
}

export interface ActivityCreate {
  title: string;
  date: string;
  category: ActivityCategory;
}

export interface Activity extends ActivityCreate {
  id: number,
}

export interface ActivityDetail extends Activity {
  headcount: number;
}

export interface ParticipBase {
  involvement: number;
  is_stuff: boolean;
}

export interface ParticipCreate extends ParticipBase {
  user: {
    label: string,
    value: number,
  };
  activity: {
    label: string,
    value: number,
  };
}

export interface Particip extends ParticipBase {
  user_id: number;
  activity_id: number;
  activity: Activity;
  participant: User;
}

export interface ParticipUpload {
  title: string;
  date: string;
  category: ActivityCategory;
  file?: File;
}
